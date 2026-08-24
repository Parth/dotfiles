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
}

fn group(env: Env, name: []const u8, description: []const u8, comptime packages: anytype) *std.Build.Step {
    const step = env.b.step(name, description);
    inline for (packages) |pkg| step.dependOn(pkg.install(env));
    return step;
}
