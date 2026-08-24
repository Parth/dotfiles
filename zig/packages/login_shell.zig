const std = @import("std");
const Env = @import("../Env.zig");
const fish = @import("fish.zig");

pub const name = "login-shell";
pub const description = "make the fish we build the login shell";

// $SHELL rather than getpwuid: build.zig is compiled without libc on linux, so
// a std.c call here fails to compile the whole build graph.
pub fn install(env: Env) *std.Build.Step {
    const b = env.b;
    const step = b.step(name, description);
    if (b.graph.host.result.os.tag == .windows) return step;

    const shell = b.pathJoin(&.{ env.prefix, "bin", "fish" });

    if (b.graph.environ_map.get("SHELL")) |current| {
        if (std.mem.eql(u8, current, shell)) return step;
    }

    // sudo so chsh does not ask PAM for a password; skipped as root, where
    // there is nothing to elevate and often no sudo. The /etc/shells line is
    // appended unconditionally -- duplicates are harmless.
    const run = b.addSystemCommand(&.{
        "/bin/sh", "-c",
        b.fmt(
            \\set -e
            \\shell="{s}"
            \\"$shell" -c 'exit 0'
            \\if [ "$(id -u)" = 0 ]; then sudo=; else sudo=sudo; fi
            \\printf '%s\n' "$shell" | $sudo tee -a /etc/shells >/dev/null
            \\$sudo chsh -s "$shell" "$(id -un)"
        , .{shell}),
    });
    run.has_side_effects = true;

    run.step.dependOn(fish.install(env));

    step.dependOn(&run.step);
    return step;
}
