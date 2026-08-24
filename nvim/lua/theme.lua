local applying = false

local function apply()
    if applying then return end
    applying = true
    local ok, err = pcall(function()
        require(vim.o.background == 'light' and 'light_theme' or 'dark_theme').colorscheme()
    end)
    applying = false
    if not ok then
        vim.notify('theme: ' .. tostring(err), vim.log.levels.ERROR)
        return
    end
    vim.api.nvim_exec_autocmds('ColorScheme', { pattern = vim.g.colors_name or '' })
end

apply()

vim.api.nvim_create_autocmd('OptionSet', {
    pattern = 'background',
    desc = 'follow the terminal between light and dark',
    callback = apply,
})

local function requery()
    pcall(vim.tty.request, '\027]11;?\007', { timeout = 500 }, function() return true end)
end

vim.api.nvim_create_autocmd({ 'FocusGained', 'VimResume' }, {
    desc = 're-ask the terminal for its background colour',
    callback = requery,
})

vim.api.nvim_create_user_command('ThemeSync', requery, {})
