return {
    'nvim-telescope/telescope.nvim', tag = '0.1.8',
    dependencies = { 'nvim-lua/plenary.nvim' },
    config = function()
      local builtin = require('telescope.builtin')
      local keymap = vim.keymap

      keymap.set('n', '<C-p>', builtin.find_files, {})
    end
}
