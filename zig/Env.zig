const std = @import("std");

b: *std.Build,
home: []const u8,
prefix: []const u8,
optimize: std.builtin.OptimizeMode,

const Env = @This();

pub fn init(b: *std.Build) Env {
    const home = b.graph.environ_map.get("HOME") orelse
        @panic("HOME is not set");
    const prefix = b.option([]const u8, "prefix", "Install prefix (default: $HOME/.local)") orelse
        b.pathJoin(&.{ home, ".local" });
    b.resolveInstallPrefix(prefix, .{});
    return .{
        .b = b,
        .home = home,
        .prefix = prefix,
        .optimize = b.option(std.builtin.OptimizeMode, "optimize", "Optimize mode for things built from source") orelse
            .ReleaseFast,
    };
}
