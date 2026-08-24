const std = @import("std");
const Env = @import("../Env.zig");
const fish = @import("fish.zig");

pub const name = "login-shell";
pub const description = "make the fish we build the login shell (asks for a password)";

// $SHELL rather than getpwuid: build.zig is compiled without libc on linux, so
// any std.c call in here is a compile error for the whole build graph, not just
// for this step.

pub fn install(env: Env) *std.Build.Step {
    const b = env.b;
    const step = b.step(name, description);
    if (b.graph.host.result.os.tag == .windows) return step;

    const shell = b.pathJoin(&.{ env.prefix, "bin", "fish" });

    if (b.graph.environ_map.get("SHELL")) |current| {
        if (std.mem.eql(u8, current, shell)) return step;
    }

    const register = if (isRegistered(b, shell)) "" else b.fmt(
        "printf '%s\\n' \"{s}\" | sudo tee -a /etc/shells >/dev/null\n",
        .{shell},
    );

    const run = b.addSystemCommand(&.{
        "/bin/sh", "-c",
        b.fmt(
            \\set -e
            \\"{0s}" -c 'exit 0'
            \\{1s}chsh -s "{0s}"
        , .{ shell, register }),
    });
    run.has_side_effects = true;

    run.step.dependOn(fish.install(env));

    step.dependOn(&run.step);
    return step;
}

fn isRegistered(b: *std.Build, shell: []const u8) bool {
    const io = b.graph.io;
    const text = std.Io.Dir.cwd().readFileAlloc(io, "/etc/shells", b.allocator, .limited(64 * 1024)) catch return false;
    var lines = std.mem.tokenizeScalar(u8, text, '\n');
    while (lines.next()) |line| {
        if (std.mem.eql(u8, std.mem.trim(u8, line, " \t\r"), shell)) return true;
    }
    return false;
}
