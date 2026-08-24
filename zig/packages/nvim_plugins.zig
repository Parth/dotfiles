const std = @import("std");
const Env = @import("../Env.zig");

pub const name = "nvim-plugins";
pub const description = "neovim plugins, pinned in build.zig.zon";

const pack = "share/nvim/site/pack/dotfiles/start";

const plugins = [_][2][]const u8{
    .{ "plenary", "plenary.nvim" },
    .{ "telescope", "telescope.nvim" },
    .{ "web_devicons", "nvim-web-devicons" },
    .{ "telescope_fzf_native", "telescope-fzf-native.nvim" },
    .{ "nvim_tree", "nvim-tree.lua" },
    .{ "gitsigns", "gitsigns.nvim" },
    .{ "illuminate", "vim-illuminate" },
};

pub fn install(env: Env) *std.Build.Step {
    const b = env.b;
    const step = b.step(name, description);

    const clear = b.addSystemCommand(&.{
        "rm", "-rf", b.pathJoin(&.{ env.prefix, pack }),
    });
    clear.has_side_effects = true;

    inline for (plugins) |p| {
        if (b.lazyDependency(p[0], .{})) |src| {
            const copy = b.addInstallDirectory(.{
                .source_dir = src.path(""),
                .install_dir = .prefix,
                .install_subdir = pack ++ "/" ++ p[1],
            });
            copy.step.dependOn(&clear.step);
            step.dependOn(&copy.step);
        }
    }

    step.dependOn(fzf_native(env, &clear.step));
    return step;
}

fn fzf_native(env: Env, after: *std.Build.Step) *std.Build.Step {
    const b = env.b;
    const step = b.step(name ++ "-fzf", "build telescope-fzf-native's C library");

    if (b.lazyDependency("telescope_fzf_native", .{})) |src| {
        const mod = b.createModule(.{
            .target = b.graph.host,
            .optimize = .ReleaseFast,
            .link_libc = true,
        });
        mod.addCSourceFiles(.{
            .root = src.path("src"),
            .files = &.{"fzf.c"},
            .flags = &.{ "-Wall", "-std=gnu99" },
        });
        const lib = b.addLibrary(.{ .name = "fzf", .linkage = .dynamic, .root_module = mod });

        const copy = b.addInstallFileWithDir(
            lib.getEmittedBin(),
            .prefix,
            pack ++ "/telescope-fzf-native.nvim/build/libfzf.so",
        );
        copy.step.dependOn(after);
        step.dependOn(&copy.step);
    }
    return step;
}
