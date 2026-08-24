const std = @import("std");
const builtin = @import("builtin");

// Claude Code ships a bare executable rather than an archive, so zig fetch
// cannot take it and it gets no build.zig.zon entry -- same shape as
// rustup-init, hence this tool. The manifest does publish a sha256 per
// platform though, so unlike fetch_rustup.zig we can verify what we got, which
// is the closest thing to the content addressing everything else here enjoys.
//
// Usage: fetch-claude <version> <output-path>

const base = "https://downloads.claude.ai/claude-code-releases";

const platform = blk: {
    const t = builtin.target;
    const arch = switch (t.cpu.arch) {
        .aarch64 => "arm64",
        .x86_64 => "x64",
        else => @compileError("no claude code build for CPU " ++ @tagName(t.cpu.arch)),
    };
    break :blk switch (t.os.tag) {
        .macos => "darwin-" ++ arch,
        // musl builds exist here, which is more than zls or lua-ls manage.
        .linux => "linux-" ++ arch ++ (if (t.abi.isMusl()) "-musl" else ""),
        .windows => "win32-" ++ arch,
        else => @compileError("no claude code build for OS " ++ @tagName(t.os.tag)),
    };
};

pub fn main(init: std.process.Init.Minimal) !void {
    var gpa_state: std.heap.DebugAllocator(.{}) = .init;
    defer _ = gpa_state.deinit();
    const gpa = gpa_state.allocator();

    var threaded: std.Io.Threaded = .init(gpa, .{
        .environ = init.environ,
        .argv0 = .init(init.args),
    });
    defer threaded.deinit();
    const io = threaded.io();

    var arena_state: std.heap.ArenaAllocator = .init(gpa);
    defer arena_state.deinit();
    const arena = arena_state.allocator();

    const args = try init.args.toSlice(arena);
    if (args.len < 3) return error.MissingArgs;
    const version = args[1];
    const out_path = args[2];

    var client: std.http.Client = .{ .allocator = gpa, .io = io };
    defer client.deinit();

    const want = try checksum(gpa, arena, &client, version);
    try download(io, arena, &client, version, out_path);

    const got = try hashFile(io, out_path);
    if (!std.mem.eql(u8, &got, &want)) {
        std.debug.print(
            "checksum mismatch for claude {s} {s}\n  want {x}\n  got  {x}\n",
            .{ version, platform, &want, &got },
        );
        return error.ChecksumMismatch;
    }

    const file = try std.Io.Dir.cwd().openFile(io, out_path, .{});
    defer file.close(io);
    try file.setPermissions(io, .executable_file);
}

/// The per-platform sha256 out of `<version>/manifest.json`.
fn checksum(gpa: std.mem.Allocator, arena: std.mem.Allocator, client: *std.http.Client, version: []const u8) ![32]u8 {
    const url = try std.fmt.allocPrint(arena, base ++ "/{s}/manifest.json", .{version});

    var body: std.Io.Writer.Allocating = .init(gpa);
    defer body.deinit();

    const res = try client.fetch(.{ .location = .{ .url = url }, .response_writer = &body.writer });
    if (res.status != .ok) {
        std.debug.print("GET {s} -> {d}\n", .{ url, @intFromEnum(res.status) });
        return error.ManifestFailed;
    }

    const parsed = try std.json.parseFromSlice(std.json.Value, arena, body.written(), .{});
    const platforms = parsed.value.object.get("platforms") orelse return error.NoPlatforms;
    const entry = platforms.object.get(platform) orelse {
        std.debug.print("claude {s} publishes no {s} build\n", .{ version, platform });
        return error.PlatformNotPublished;
    };
    const hex = (entry.object.get("checksum") orelse return error.NoChecksum).string;

    var out: [32]u8 = undefined;
    _ = try std.fmt.hexToBytes(&out, hex);
    return out;
}

fn download(io: std.Io, arena: std.mem.Allocator, client: *std.http.Client, version: []const u8, out_path: []const u8) !void {
    const url = try std.fmt.allocPrint(arena, base ++ "/{s}/" ++ platform ++ "/claude", .{version});

    const file = try std.Io.Dir.cwd().createFile(io, out_path, .{});
    defer file.close(io);

    var buf: [256 * 1024]u8 = undefined;
    var fw = file.writer(io, &buf);

    const res = try client.fetch(.{ .location = .{ .url = url }, .response_writer = &fw.interface });
    if (res.status != .ok) {
        std.debug.print("GET {s} -> {d}\n", .{ url, @intFromEnum(res.status) });
        return error.DownloadFailed;
    }
    try fw.interface.flush();
}

/// Streamed rather than read whole: the binary is around 295 MB.
fn hashFile(io: std.Io, path: []const u8) ![32]u8 {
    const file = try std.Io.Dir.cwd().openFile(io, path, .{});
    defer file.close(io);

    var buf: [256 * 1024]u8 = undefined;
    var fr = file.reader(io, &buf);

    var hasher = std.crypto.hash.sha2.Sha256.init(.{});
    var chunk: [256 * 1024]u8 = undefined;
    while (true) {
        // readSliceShort reports EOF as a short read, not an error.
        const n = try fr.interface.readSliceShort(&chunk);
        if (n == 0) break;
        hasher.update(chunk[0..n]);
    }

    var out: [32]u8 = undefined;
    hasher.final(&out);
    return out;
}
