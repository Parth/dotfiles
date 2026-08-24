const std = @import("std");
const Env = @import("../Env.zig");

pub const name = "zls";
pub const description = "the zig language server, from its prebuilt release";

pub fn install(env: Env) *std.Build.Step {
    const b = env.b;
    const step = b.step(name, description);

    const host = b.graph.host.result;
    const dep_name = switch (host.os.tag) {
        .macos => switch (host.cpu.arch) {
            .aarch64 => "zls_macos_aarch64",
            .x86_64 => "zls_macos_x86_64",
            else => return step,
        },
        .linux => switch (host.cpu.arch) {
            .aarch64 => "zls_linux_aarch64",
            .x86_64 => "zls_linux_x86_64",
            else => return step,
        },
        else => return step,
    };

    if (b.lazyDependency(dep_name, .{})) |src| {
        step.dependOn(&b.addInstallBinFile(src.path("zls"), "zls").step);
    }
    return step;
}
