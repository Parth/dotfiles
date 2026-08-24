const std = @import("std");
const builtin = @import("builtin");

const rust_host = blk: {
    const t = builtin.target;
    const arch = switch (t.cpu.arch) {
        .aarch64 => "aarch64",
        .x86_64 => "x86_64",
        else => @compileError("no rust host triple for CPU " ++ @tagName(t.cpu.arch)),
    };
    break :blk switch (t.os.tag) {
        .macos => arch ++ "-apple-darwin",
        .linux => arch ++ if (t.abi.isMusl()) "-unknown-linux-musl" else "-unknown-linux-gnu",
        .windows => arch ++ "-pc-windows-msvc",
        else => @compileError("no rust host triple for OS " ++ @tagName(t.os.tag)),
    };
};

const installer_name = "rustup-init" ++ if (builtin.target.os.tag == .windows) ".exe" else "";
const url = "https://static.rust-lang.org/rustup/dist/" ++ rust_host ++ "/" ++ installer_name;

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

    const args = try init.args.toSlice(arena_state.allocator());
    if (args.len < 2) return error.MissingOutputPath;

    var client: std.http.Client = .{ .allocator = gpa, .io = io };
    defer client.deinit();

    const file = try std.Io.Dir.cwd().createFile(io, args[1], .{});
    defer file.close(io);

    var buf: [64 * 1024]u8 = undefined;
    var fw = file.writer(io, &buf);

    const res = try client.fetch(.{
        .location = .{ .url = url },
        .response_writer = &fw.interface,
    });
    if (res.status != .ok) {
        std.debug.print("GET {s} -> {d}\n", .{ url, @intFromEnum(res.status) });
        return error.DownloadFailed;
    }
    try fw.interface.flush();
    try file.setPermissions(io, .executable_file);
}
