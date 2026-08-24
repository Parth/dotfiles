const std = @import("std");
const Env = @import("../Env.zig");

pub const name = "lua-ls";
pub const description = "lua-language-server, from its prebuilt release";

const subdir = "share/lua-language-server";

pub fn install(env: Env) *std.Build.Step {
    const b = env.b;
    const step = b.step(name, description);

    const host = b.graph.host.result;
    const dep_name = switch (host.os.tag) {
        .macos => switch (host.cpu.arch) {
            .aarch64 => "lua_ls_macos_aarch64",
            .x86_64 => "lua_ls_macos_x86_64",
            else => return step,
        },
        .linux => switch (host.cpu.arch) {
            .aarch64 => "lua_ls_linux_aarch64",
            .x86_64 => "lua_ls_linux_x86_64",
            else => return step,
        },
        else => return step,
    };

    if (b.lazyDependency(dep_name, .{})) |src| {
        step.dependOn(&b.addInstallDirectory(.{
            .source_dir = src.path(""),
            .install_dir = .prefix,
            .install_subdir = subdir,
        }).step);
    }
    return step;
}
