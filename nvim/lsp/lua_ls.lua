return {
    cmd = { vim.env.HOME .. '/.local/share/lua-language-server/bin/lua-language-server' },
    filetypes = { 'lua' },
    root_markers = { '.luarc.json', '.git' },
    settings = {
        Lua = {
            runtime = { version = 'LuaJIT' },
            diagnostics = { globals = { 'vim', 'require' } },
            workspace = { library = { vim.env.VIMRUNTIME .. '/lua' } },
            telemetry = { enable = false },
        },
    },
}
