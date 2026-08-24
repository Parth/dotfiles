const std = @import("std");
const Env = @import("../Env.zig");

pub const name = "rust";
pub const description = "rustup and a minimal toolchain, fetched by zig alone";

var cached: ?*std.Build.Step = null;

pub fn cargo(env: Env) []const u8 {
    return env.b.pathJoin(&.{ env.home, ".cargo", "bin", "cargo" });
}

pub fn install(env: Env) *std.Build.Step {
    if (cached) |step| return step;
    const b = env.b;

    const fetcher = b.addExecutable(.{
        .name = "fetch-rustup",
        .root_module = b.createModule(.{
            .root_source_file = b.path("zig/tools/fetch_rustup.zig"),
            .target = b.graph.host,
            .optimize = .ReleaseSafe,
        }),
    });

    const download = b.addRunArtifact(fetcher);
    const installer = download.addOutputFileArg("rustup-init");

    const run = std.Build.Step.Run.create(b, "rustup-init");
    run.addFileArg(installer);
    run.addArgs(&.{ "-y", "--no-modify-path", "--profile", "minimal" });
    if (b.args) |extra| run.addArgs(extra);
    run.has_side_effects = true;

    const analyzer = b.addSystemCommand(&.{
        b.pathJoin(&.{ env.home, ".cargo", "bin", "rustup" }),
        "component",
        "add",
        "rust-analyzer",
    });
    analyzer.has_side_effects = true;
    analyzer.step.dependOn(&run.step);

    const step = b.step(name, description);
    step.dependOn(&analyzer.step);
    cached = step;
    return step;
}
