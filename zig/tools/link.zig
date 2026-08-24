const std = @import("std");

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
    const cwd = std.Io.Dir.cwd();

    var i: usize = 1;
    while (i + 1 < args.len) : (i += 2) {
        const target = args[i];
        const link = args[i + 1];

        if (std.fs.path.dirname(link)) |parent| {
            try cwd.createDirPath(io, parent);
        }

        var buf: [std.fs.max_path_bytes]u8 = undefined;
        if (cwd.readLink(io, link, &buf)) |n| {
            if (std.mem.eql(u8, buf[0..n], target)) continue;
        } else |err| switch (err) {
            error.FileNotFound => {},
            error.NotLink => {
                std.debug.print("refusing to replace non-symlink: {s}\n", .{link});
                return error.PathOccupied;
            },
            else => |e| return e,
        }

        try cwd.symLinkAtomic(io, target, link, .{});
        std.debug.print("linked {s}\n", .{link});
    }
}
