vim.g.mapleader = ' '

require("config")
require("theme")
require("treesitter")
require("plugins")
require("keyboard")
require("ui")

vim.opt.completeopt = { 'menu', 'menuone', 'noselect', 'popup', 'fuzzy' }

vim.lsp.enable({ 'rust_analyzer', 'lua_ls', 'zls' })

vim.api.nvim_create_user_command('LspLog', function() vim.cmd.tabnew(vim.lsp.log.get_filename()) end, {})
