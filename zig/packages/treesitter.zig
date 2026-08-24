const std = @import("std");
const Env = @import("../Env.zig");

pub const name = "treesitter";
pub const description = "tree-sitter grammars, compiled by zig";

pub const Grammar = struct {
    lang: []const u8,
    dep: []const u8,
    scanner: bool = false,
    flags: []const []const u8 = &.{},
};

pub const grammars = [_]Grammar{
    .{ .lang = "rust", .dep = "ts_rust", .scanner = true },
    .{ .lang = "zig", .dep = "ts_zig" },
    .{ .lang = "nix", .dep = "ts_nix", .scanner = true },
    .{ .lang = "toml", .dep = "ts_toml", .scanner = true },
    .{ .lang = "json", .dep = "ts_json" },
    .{ .lang = "bash", .dep = "ts_bash", .scanner = true },
    .{ .lang = "fish", .dep = "ts_fish", .scanner = true },
    .{ .lang = "yaml", .dep = "ts_yaml", .scanner = true, .flags = &.{"-DYAML_SCHEMA=core"} },
};

pub fn install(env: Env) *std.Build.Step {
    const b = env.b;
    const step = b.step(name, description);

    inline for (grammars) |g| step.dependOn(parser(env, g));
    step.dependOn(queries(env));
    return step;
}

fn parser(env: Env, comptime g: Grammar) *std.Build.Step {
    const b = env.b;
    const step = b.step("ts-" ++ g.lang, "build the " ++ g.lang ++ " parser");

    if (b.lazyDependency(g.dep, .{})) |src| {
        const mod = b.createModule(.{
            .target = b.graph.host,
            .optimize = .ReleaseFast,
            .link_libc = true,
        });
        mod.addIncludePath(src.path("src"));
        mod.addCSourceFiles(.{
            .root = src.path("src"),
            .files = if (g.scanner) &.{ "parser.c", "scanner.c" } else &.{"parser.c"},
            .flags = g.flags,
        });

        const lib = b.addLibrary(.{ .name = g.lang, .linkage = .dynamic, .root_module = mod });
        step.dependOn(&b.addInstallFileWithDir(
            lib.getEmittedBin(),
            .prefix,
            "share/nvim/site/parser/" ++ g.lang ++ ".so",
        ).step);
    }
    return step;
}

fn queries(env: Env) *std.Build.Step {
    const b = env.b;
    const step = b.step("ts-queries", "install nvim-treesitter's queries");

    if (b.lazyDependency("nvim_treesitter_queries", .{})) |src| {
        step.dependOn(&b.addInstallDirectory(.{
            .source_dir = src.path("runtime/queries"),
            .install_dir = .prefix,
            .install_subdir = "share/nvim/site/queries",
        }).step);
    }
    return step;
}
