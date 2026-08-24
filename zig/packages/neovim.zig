const std = @import("std");
const Env = @import("../Env.zig");

pub const name = "nvim";
pub const description = "neovim, built from pinned source";

pub fn install(env: Env) *std.Build.Step {
    const b = env.b;
    const src = b.dependency("neovim", .{});

    const run = b.addSystemCommand(&.{ b.graph.zig_exe, "build", "--build-file" });
    run.addFileArg(src.path("build.zig"));
    run.addArgs(&.{
        "--cache-dir",
        b.pathFromRoot(".zig-cache-nvim"),
        "--prefix",
        env.prefix,
        "install",
        b.fmt("-Doptimize={s}", .{@tagName(env.optimize)}),
        b.fmt("-Dinstall-path={s}", .{env.prefix}),
    });
    run.has_side_effects = true;

    const step = b.step(name, description);
    step.dependOn(&run.step);
    return step;
}
