const std = @import("std");
const Env = @import("../Env.zig");

pub const name = "brew";
pub const description = "homebrew, and everything in the Brewfile";

const brew = "/opt/homebrew/bin/brew";
const installer = "https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh";

pub fn install(env: Env) *std.Build.Step {
    const b = env.b;
    const step = b.step(name, description);
    if (b.graph.host.result.os.tag != .macos) return step;

    const bootstrap = b.addSystemCommand(&.{ "/bin/bash", "-c", b.fmt(
        "test -x {s} || /bin/bash -c \"$(curl -fsSL {s})\"",
        .{ brew, installer },
    ) });
    bootstrap.has_side_effects = true;

    step.dependOn(bundle(env, &bootstrap.step, "--no-upgrade"));

    const upgrade = b.step(name ++ "-upgrade", "upgrade everything in the Brewfile");
    upgrade.dependOn(bundle(env, &bootstrap.step, "--upgrade"));

    return step;
}

fn bundle(env: Env, after: *std.Build.Step, flag: []const u8) *std.Build.Step {
    const b = env.b;
    const run = b.addSystemCommand(&.{ brew, "bundle", "install", flag, "--file" });
    run.addFileArg(b.path("Brewfile"));
    run.has_side_effects = true;
    run.step.dependOn(after);
    return &run.step;
}
