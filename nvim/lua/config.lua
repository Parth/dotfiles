vim.opt.nu = true

vim.opt.tabstop = 4
vim.opt.softtabstop = 4
vim.opt.shiftwidth = 4
vim.opt.expandtab = true
vim.opt.smartindent = true

vim.opt.swapfile = false
vim.opt.backup = false
vim.opt.undodir = os.getenv("HOME") .. "/.vim/undodir"
vim.opt.undofile = true

vim.opt.hlsearch = true
vim.opt.incsearch = true

vim.opt.cursorline = true

vim.opt.autoread = true
vim.opt.updatetime = 250

local disk = vim.api.nvim_create_augroup('disk', { clear = true })

vim.api.nvim_create_autocmd({ 'FocusGained', 'BufEnter', 'CursorHold', 'TermClose', 'TermLeave' }, {
    group = disk,
    desc = 'pick up edits made outside nvim',
    callback = function()
        if vim.bo.buftype == '' and vim.fn.mode() ~= 'c' then
            vim.schedule(function() vim.cmd.checktime() end)
        end
    end,
})

vim.api.nvim_create_autocmd('FileChangedShellPost', {
    group = disk,
    desc = 'say so when a buffer is reloaded underneath you',
    callback = function()
        vim.notify(vim.fn.expand('<afile>:.') .. ' changed on disk', vim.log.levels.WARN)
    end,
})
