const std = @import("std");
const Env = @import("../Env.zig");

pub const name = "claude-code";
pub const description = "claude code, pinned and self-update disabled";

// Pinned, like everything else here. That takes an argument with the tool
// itself, which ships a native updater: it writes
// ~/.local/share/claude/versions/<v> and repoints ~/.local/bin/claude, the
// exact path this step installs to. Left alone the two fight, and whatever
// version is written below becomes fiction on the first update.
//
// So fish/conf.d/dotfiles.fish exports DISABLE_AUTOUPDATER=1 and this is the
// only thing that moves it. Bump here, rebuild, done -- the same deal as
// neovim, fish and zls.
//
//   stable channel: https://downloads.claude.ai/claude-code-releases/stable
const version = "2.1.231";

pub fn install(env: Env) *std.Build.Step {
    const b = env.b;
    const step = b.step(name, description);

    const host = b.graph.host.result;
    switch (host.os.tag) {
        .macos, .linux, .windows => {},
        else => return step,
    }

    const fetcher = b.addExecutable(.{
        .name = "fetch-claude",
        .root_module = b.createModule(.{
            .root_source_file = b.path("zig/tools/fetch_claude.zig"),
            .target = b.graph.host,
            .optimize = .ReleaseSafe,
        }),
    });

    const run = b.addRunArtifact(fetcher);
    run.addArg(version);
    const binary = run.addOutputFileArg("claude");

    step.dependOn(&b.addInstallBinFile(binary, "claude").step);
    return step;
}
