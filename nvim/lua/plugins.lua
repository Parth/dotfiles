local telescope = require('telescope')

telescope.setup {
    extensions = {
        fzf = { fuzzy = true, override_generic_sorter = true, override_file_sorter = true },
    },
}

telescope.load_extension('fzf')

vim.g.loaded_netrw = 1
vim.g.loaded_netrwPlugin = 1
require('nvim-tree').setup({
    diagnostics = {
        enable = true
    }
})

require('gitsigns').setup {
    current_line_blame = true,
}

require('illuminate').configure {}
