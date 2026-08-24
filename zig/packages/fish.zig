const std = @import("std");
const Env = @import("../Env.zig");
const rust = @import("rust.zig");

pub const name = "fish";
pub const description = "fish shell, built from pinned source with cargo";

var cached: ?*std.Build.Step = null;

pub fn install(env: Env) *std.Build.Step {
    if (cached) |step| return step;
    const b = env.b;
    const src = b.dependency("fish", .{});
    const out = b.pathFromRoot(".zig-cache-fish");

    const build_fish = b.addSystemCommand(&.{ rust.cargo(env), "build", "--release", "--locked", "--bin", "fish", "--target-dir", out, "--manifest-path" });
    build_fish.addFileArg(src.path("Cargo.toml"));
    build_fish.setEnvironmentVariable("PREFIX", env.prefix);
    build_fish.setEnvironmentVariable("CARGO_HOME", b.pathJoin(&.{ env.home, ".cargo" }));
    build_fish.has_side_effects = true;
    build_fish.step.dependOn(rust.install(env));

    const copy = b.addInstallBinFile(b.path(".zig-cache-fish/release/fish"), "fish");
    copy.step.dependOn(&build_fish.step);

    const step = b.step(name, description);
    step.dependOn(&copy.step);
    cached = step;
    return step;
}
