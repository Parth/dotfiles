vim.diagnostic.config({
    virtual_text = { prefix = '\u{f444}', spacing = 2 },
    signs = true,
    underline = true,
    severity_sort = true,
    float = { border = 'rounded', source = true },
})

local groups = {
    SlModeN    = { fg = '#000000', bg = '#66B2FF', bold = true },
    SlModeI    = { fg = '#1A1A1A', bg = '#FFDB70', bold = true },
    SlModeV    = { fg = '#1A1A1A', bg = '#AC8CD9', bold = true },
    SlModeR    = { fg = '#1A1A1A', bg = '#FF6680', bold = true },
    SlModeC    = { fg = '#1A1A1A', bg = '#6EECF7', bold = true },
    SlB        = { fg = '#FFFFFF', bg = '#242424' },
    SlC        = { fg = '#FFFFFF', bg = '#1A1A1A' },
    SlAdded    = { fg = '#67E4B6', bg = '#2A2A2A' },
    SlModified = { fg = '#66B2FF', bg = '#2A2A2A' },
    SlRemoved  = { fg = '#FF6680', bg = '#2A2A2A' },
    SlGit      = { fg = '#FFFFFF', bg = '#2A2A2A' },
    WbPath     = { fg = '#FFFFFF', bg = '#2A2A2A' },
    WbError    = { fg = '#FF6680', bg = '#2A2A2A' },
    WbWarn     = { fg = '#FFDB70', bg = '#2A2A2A' },
    WbInfo     = { fg = '#6EECF7', bg = '#2A2A2A' },
    WbHint     = { fg = '#D0D0D0', bg = '#2A2A2A' },
    IlluminatedWordText  = { underline = true },
    IlluminatedWordRead  = { underline = true },
    IlluminatedWordWrite = { underline = true, bold = true },
}

local function paint()
    for name, spec in pairs(groups) do vim.api.nvim_set_hl(0, name, spec) end
end

paint()
vim.api.nvim_create_autocmd('ColorScheme', { desc = 'themes clear highlights', callback = paint })

local MODES = {
    n = { 'NORMAL', 'SlModeN' },   i = { 'INSERT', 'SlModeI' },
    v = { 'VISUAL', 'SlModeV' },   V = { 'V-LINE', 'SlModeV' },
    ['\22'] = { 'V-BLOCK', 'SlModeV' },
    s = { 'SELECT', 'SlModeV' },   S = { 'S-LINE', 'SlModeV' },
    R = { 'REPLACE', 'SlModeR' },  c = { 'COMMAND', 'SlModeC' },
    t = { 'TERMINAL', 'SlModeC' }, ['!'] = { 'SHELL', 'SlModeC' },
}

function _G.sl_mode()
    local m = MODES[vim.api.nvim_get_mode().mode:sub(1, 1)] or { 'NORMAL', 'SlModeN' }
    return ('%%#%s# %s %%#SlB#'):format(m[2], m[1])
end

function _G.sl_git()
    local d = vim.b.gitsigns_status_dict
    if not d then return '' end
    local out = { '%#SlGit# \u{e0a0} ' .. (d.head or '') .. ' ' }
    local parts = {
        { 'SlAdded', '\u{f0fe} ', d.added },
        { 'SlModified', '\u{f14b} ', d.changed },
        { 'SlRemoved', '\u{f146} ', d.removed },
    }
    for _, p in ipairs(parts) do
        if (p[3] or 0) > 0 then out[#out + 1] = ('%%#%s#%s%d '):format(p[1], p[2], p[3]) end
    end
    return table.concat(out) .. '%#SlB#'
end

function _G.sl_lsp()
    local names = {}
    for _, c in ipairs(vim.lsp.get_clients({ bufnr = 0 })) do names[#names + 1] = c.name end
    return #names > 0 and (' ' .. table.concat(names, ',') .. ' ') or ''
end

vim.opt.laststatus = 2
vim.opt.statusline = table.concat({
    '%{%v:lua.sl_mode()%}',
    '%{%v:lua.sl_git()%}',
    '%#SlC#%=',
    '%#SlB#%{%v:lua.sl_lsp()%}',
    '%#SlB# %{&filetype} ',
    '%#SlModeN# %l:%c ',
})

function _G.wb_path()
    local name = vim.api.nvim_buf_get_name(0)
    if name == '' then return '[No Name]' end
    local p = vim.fn.fnamemodify(name, ':p:~')
    if vim.bo.readonly then p = p .. ' \u{e0a2}' end
    if vim.bo.modified then p = p .. ' \u{25cf}' end
    return p
end

function _G.wb_diag()
    local n = vim.diagnostic.count(0)
    local S, out = vim.diagnostic.severity, {}
    local parts = {
        { 'WbError', '\u{f057} ', n[S.ERROR] },
        { 'WbWarn', '\u{f071} ', n[S.WARN] },
        { 'WbInfo', '\u{f05a} ', n[S.INFO] },
        { 'WbHint', '\u{f400} ', n[S.HINT] },
    }
    for _, p in ipairs(parts) do
        if (p[3] or 0) > 0 then out[#out + 1] = ('%%#%s#%s%d '):format(p[1], p[2], p[3]) end
    end
    return #out > 0 and (table.concat(out) .. '%#Normal#') or ''
end

vim.opt.winbar = '%#WbPath# %{%v:lua.wb_path()%} %#Normal#%=%{%v:lua.wb_diag()%}'

vim.api.nvim_create_autocmd('LspProgress', {
    callback = function(ev)
        local c = vim.lsp.get_client_by_id(ev.data.client_id)
        local name = c and c.name or 'lsp'
        local v = ev.data.params.value
        if v.kind == 'end' then
            vim.notify(name .. ': ' .. (v.title or '') .. ' done')
        elseif v.percentage then
            print(string.format('%s: %s %d%%', name, v.title or '', v.percentage))
        end
    end,
})

vim.api.nvim_create_autocmd('LspAttach', {
    callback = function(ev)
        local c = vim.lsp.get_client_by_id(ev.data.client_id)
        if not c then return end
        vim.notify('LSP attached: ' .. c.name, vim.log.levels.INFO)
        vim.cmd('redrawstatus')
    end,
})

vim.api.nvim_create_user_command('LspStatus', function()
    local cs = vim.lsp.get_clients({ bufnr = 0 })
    if #cs == 0 then
        print('NO CLIENT attached to this buffer. filetype=' .. vim.bo.filetype)
        return
    end
    for _, c in ipairs(cs) do
        print(string.format('%s  id=%d  root=%s', c.name, c.id, c.root_dir or '?'))
    end
    print('diagnostics: ' .. #vim.diagnostic.get(0))
end, {})
