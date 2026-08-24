const std = @import("std");
const Env = @import("zig/Env.zig");

// Everything here has to run start to finish with nobody watching: no password
// prompt, no tty, no machine state changed outside the install prefix. That is
// what makes `zig build headless` the one command CI runs.
const headless = .{
    @import("zig/packages/neovim.zig"),
    @import("zig/packages/rust.zig"),
    @import("zig/packages/fish.zig"),
    @import("zig/packages/lua_ls.zig"),
    @import("zig/packages/zls.zig"),
    @import("zig/packages/ripgrep.zig"),
    @import("zig/packages/nvim_plugins.zig"),
    @import("zig/packages/treesitter.zig"),
    @import("zig/packages/config.zig"),
};

// chsh wants a PAM password and writes to /etc/shells. Nothing unattended can
// do that, so it is its own group rather than a footnote in headless.
const interactive = .{
    @import("zig/packages/login_shell.zig"),
};

const gui = .{
    @import("zig/packages/brew.zig"),
};

pub fn build(b: *std.Build) void {
    const env = Env.init(b);
    const all = b.getInstallStep();

    all.dependOn(group(env, "headless", "everything that installs unattended", headless));
    all.dependOn(group(env, "interactive", "steps that will prompt you", interactive));
    all.dependOn(group(env, "gui", "desktop applications", gui));

    smoke(env);
}

fn group(env: Env, name: []const u8, description: []const u8, comptime packages: anytype) *std.Build.Step {
    const step = env.b.step(name, description);
    inline for (packages) |pkg| step.dependOn(pkg.install(env));
    return step;
}

// `zig build smoke` asks the installed tree whether it works, which is a
// different question from whether it built. It deliberately does not depend on
// the headless step: after an install you want to re-check without rebuilding,
// and in CI a smoke failure should be a separate red square from a build one.
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
