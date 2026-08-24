const std = @import("std");
const Env = @import("zig/Env.zig");

const headless = .{
    @import("zig/packages/neovim.zig"),
    @import("zig/packages/rust.zig"),
    @import("zig/packages/fish.zig"),
    @import("zig/packages/login_shell.zig"),
    @import("zig/packages/lua_ls.zig"),
    @import("zig/packages/zls.zig"),
    @import("zig/packages/ripgrep.zig"),
    @import("zig/packages/claude_code.zig"),
    @import("zig/packages/nvim_plugins.zig"),
    @import("zig/packages/treesitter.zig"),
    @import("zig/packages/config.zig"),
};

const gui = .{
    @import("zig/packages/brew.zig"),
};

pub fn build(b: *std.Build) void {
    const env = Env.init(b);
    const all = b.getInstallStep();

    all.dependOn(group(env, "headless", "everything that runs without a display", headless));
    all.dependOn(group(env, "gui", "desktop applications", gui));

    smoke(env);
}

fn group(env: Env, name: []const u8, description: []const u8, comptime packages: anytype) *std.Build.Step {
    const step = env.b.step(name, description);
    inline for (packages) |pkg| step.dependOn(pkg.install(env));
    return step;
}

// Deliberately independent of the headless step, so it can re-check an
// existing install without rebuilding.
fn smoke(env: Env) void {
    const b = env.b;

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("zig/smoke.zig"),
            .target = b.graph.host,
            .optimize = .Debug,
        }),
    });

    const run = b.addRunArtifact(tests);
    run.setEnvironmentVariable("DOTFILES_PREFIX", env.prefix);
    run.has_side_effects = true;

    b.step("smoke", "check that an installed dotfiles actually works").dependOn(&run.step);
}
