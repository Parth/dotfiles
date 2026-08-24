return {
    cmd = { vim.env.HOME .. '/.local/bin/zls' },
    filetypes = { 'zig', 'zon' },
    root_markers = { 'build.zig', 'build.zig.zon', '.git' },
    settings = {
        zls = {
            enable_build_on_save = true,
            semantic_tokens = 'partial',
        },
    },
}
