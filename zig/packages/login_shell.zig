const std = @import("std");
const Env = @import("../Env.zig");
const fish = @import("fish.zig");

pub const name = "login-shell";
pub const description = "make the fish we build the login shell";

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

    // chsh as an ordinary user asks PAM for a password, which needs a terminal
    // and so cannot run unattended. Under sudo it does not ask, and sudo was
    // already required here to append to /etc/shells. As root -- every
    // container -- there is nothing to elevate and no sudo to elevate with, so
    // decide at run time rather than baking one of the two in.
    //
    // The /etc/shells line is appended without checking whether it is already
    // there. Duplicates cost nothing: getusershell() enumerates the file and
    // every consumer is asking "is this shell in here", so a repeated line is
    // answered the same way as a single one. Nothing depends on the append
    // either -- chsh only consults /etc/shells for non-root callers, and this
    // one is always root -- so it is here to keep the file honest about which
    // shells are login shells, not to make the next line work.
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
