//! Smoke tests for an installed dotfiles tree, run against $DOTFILES_PREFIX.
//!
//! The lists come from the packages themselves, so adding a grammar or a
//! plugin extends the tests without touching this file.

const std = @import("std");
const testing = std.testing;

const config = @import("packages/config.zig");
const lua_ls = @import("packages/lua_ls.zig");
const nvim_plugins = @import("packages/nvim_plugins.zig");
const treesitter = @import("packages/treesitter.zig");

const gpa = testing.allocator;

fn env(key: []const u8) ?[]const u8 {
    return testing.environ.getPosix(key);
}

fn prefix() []const u8 {
    return env("DOTFILES_PREFIX") orelse
        @panic("DOTFILES_PREFIX is not set; run this as `zig build smoke`");
}

const Path = struct {
    buf: [std.fs.max_path_bytes]u8 = undefined,

    /// Resolve a path relative to the install prefix.
    fn in(p: *Path, parts: []const []const u8) []const u8 {
        var w: std.Io.Writer = .fixed(&p.buf);
        w.writeAll(prefix()) catch @panic("path too long");
        for (parts) |part| {
            w.writeByte('/') catch @panic("path too long");
            w.writeAll(part) catch @panic("path too long");
        }
        return w.buffered();
    }

    /// Resolve a path relative to $HOME, for the rustup files outside the prefix.
    fn home(p: *Path, parts: []const []const u8) []const u8 {
        var w: std.Io.Writer = .fixed(&p.buf);
        w.writeAll(env("HOME") orelse @panic("HOME is not set")) catch @panic("path too long");
        for (parts) |part| {
            w.writeByte('/') catch @panic("path too long");
            w.writeAll(part) catch @panic("path too long");
        }
        return w.buffered();
    }
};

fn expectExists(path: []const u8, options: std.Io.Dir.AccessOptions) !void {
    std.Io.Dir.cwd().access(testing.io, path, options) catch |err| {
        std.debug.print("missing: {s} ({s})\n", .{ path, @errorName(err) });
        return error.NotInstalled;
    };
}

/// Run a command and require a clean exit. `needle` may appear on either
/// stream, since tools disagree about where to print a version. The timeout is
/// because a language server given arguments it dislikes waits on stdin.
fn expectRun(argv: []const []const u8, needle: ?[]const u8) !void {
    const result = std.process.run(gpa, testing.io, .{
        .argv = argv,
        .timeout = .{ .duration = .{ .raw = .fromSeconds(60), .clock = .awake } },
    }) catch |err| {
        std.debug.print("could not run {s}: {s}\n", .{ argv[0], @errorName(err) });
        return error.CommandFailed;
    };
    defer gpa.free(result.stdout);
    defer gpa.free(result.stderr);

    const failed = switch (result.term) {
        .exited => |code| code != 0,
        else => true,
    };
    if (failed or (needle != null and
        std.mem.indexOf(u8, result.stdout, needle.?) == null and
        std.mem.indexOf(u8, result.stderr, needle.?) == null))
    {
        std.debug.print(
            \\command: {s}
            \\term: {any}
            \\stdout: {s}
            \\stderr: {s}
            \\
        , .{ argv[0], result.term, result.stdout, result.stderr });
        if (failed) return error.CommandFailed;
        std.debug.print("expected the output to mention \"{s}\"\n", .{needle.?});
        return error.UnexpectedOutput;
    }
}

test "the binaries we install run" {
    var p: Path = .{};

    try expectRun(&.{ p.in(&.{ "bin", "nvim" }), "--version" }, "NVIM");
    try expectRun(&.{ p.in(&.{ "bin", "rg" }), "--version" }, "ripgrep");
    try expectRun(&.{ p.in(&.{ "bin", "zls" }), "--version" }, null);
    try expectRun(&.{ p.in(&.{ "bin", "fish" }), "--version" }, "fish");
    try expectRun(&.{ p.home(&.{ ".cargo", "bin", "cargo" }), "--version" }, "cargo");

    // Run it rather than stat it: this is the only dynamically linked binary
    // we install, so present and runnable are different questions.
    try expectRun(&.{ p.in(&.{ lua_ls.subdir, "bin", "lua-language-server" }), "--version" }, null);
}

test "rust-analyzer is in the toolchain" {
    var p: Path = .{};
    try expectRun(
        &.{ p.home(&.{ ".cargo", "bin", "rustup" }), "component", "list", "--installed" },
        "rust-analyzer",
    );
}

test "every config link resolves" {
    var p: Path = .{};
    var buf: [std.fs.max_path_bytes]u8 = undefined;

    for (config.links) |link| {
        const path = p.home(&.{link[1]});

        // readLink proves it is ours rather than a file that happened to be
        // there; access follows it, which proves the far end still exists.
        _ = std.Io.Dir.cwd().readLink(testing.io, path, &buf) catch |err| {
            std.debug.print("not a symlink: {s} ({s})\n", .{ path, @errorName(err) });
            return error.NotLinked;
        };
        try expectExists(path, .{});
    }
}

test "every plugin is unpacked" {
    var p: Path = .{};

    for (nvim_plugins.plugins) |plugin| {
        try expectExists(p.in(&.{ nvim_plugins.pack, plugin[1] }), .{});
    }

    // Telescope silently falls back to a slow pure-lua sorter without this.
    try expectExists(
        p.in(&.{ nvim_plugins.pack, "telescope-fzf-native.nvim", "build", "libfzf.so" }),
        .{},
    );
}

test "every grammar is compiled" {
    var p: Path = .{};

    inline for (treesitter.grammars) |grammar| {
        try expectExists(p.in(&.{ "share/nvim/site/parser", grammar.lang ++ ".so" }), .{});
        try expectExists(p.in(&.{ "share/nvim/site/queries", grammar.lang }), .{});
    }
}

/// nvim --headless writes ordinary messages to stderr, so :messages has to be
/// read back and scanned instead.
const startup =
    "lua local out = vim.api.nvim_exec2('messages', {output=true}).output " ++
    "io.stdout:write(out) " ++
    "if out:match('E%d+:') or out:match('Error detected') or out:match('Error executing') " ++
    "then vim.cmd('cq') end";

test "nvim starts clean with the shipped config" {
    var p: Path = .{};
    try expectRun(&.{ p.in(&.{ "bin", "nvim" }), "--headless", "-c", startup, "+qa" }, null);
}

/// Installed is not loadable: a wrong-ABI grammar only fails here.
const load_parsers = blk: {
    var langs: []const u8 = "";
    for (treesitter.grammars, 0..) |grammar, i| {
        langs = langs ++ (if (i == 0) "" else ",") ++ "'" ++ grammar.lang ++ "'";
    }
    break :blk "lua local bad = {} " ++
        "for _, lang in ipairs({" ++ langs ++ "}) do " ++
        "local ok, err = pcall(vim.treesitter.language.add, lang) " ++
        "if not ok then bad[#bad+1] = lang .. ': ' .. tostring(err) end end " ++
        "if #bad > 0 then io.stdout:write(table.concat(bad, '\\n')) vim.cmd('cq') end";
};

test "nvim loads every grammar" {
    var p: Path = .{};
    try expectRun(&.{ p.in(&.{ "bin", "nvim" }), "--headless", "-c", load_parsers, "+qa" }, null);
}

test "fish runs the shipped config" {
    var p: Path = .{};
    // Set by conf.d; empty if the symlink or fish_add_path broke.
    try expectRun(&.{ p.in(&.{ "bin", "fish" }), "-l", "-c", "echo $EDITOR" }, "nvim");
}
