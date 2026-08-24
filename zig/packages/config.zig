const std = @import("std");
const Env = @import("../Env.zig");

pub const name = "config";
pub const description = "symlink dotfiles into ~/.config";

const links = [_][2][]const u8{
    .{ "fish/conf.d/dotfiles.fish", ".config/fish/conf.d/dotfiles.fish" },
    .{ "wezterm", ".config/wezterm" },
    .{ "nvim", ".config/nvim" },
    .{ "sway", ".config/sway" },
    .{ "git/config", ".config/git/config" },
};

pub fn install(env: Env) *std.Build.Step {
    const b = env.b;

    const linker = b.addExecutable(.{
        .name = "link",
        .root_module = b.createModule(.{
            .root_source_file = b.path("zig/tools/link.zig"),
            .target = b.graph.host,
            .optimize = .ReleaseSafe,
        }),
    });

    const run = b.addRunArtifact(linker);
    for (links) |l| {
        run.addArgs(&.{ b.pathFromRoot(l[0]), b.pathJoin(&.{ env.home, l[1] }) });
    }
    run.has_side_effects = true;

    const step = b.step(name, description);
    step.dependOn(&run.step);
    return step;
}
