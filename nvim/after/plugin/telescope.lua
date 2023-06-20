local builtin = require('telescope.builtin')
vim.keymap.set('n', '<leader>T', builtin.find_files, {})
vim.keymap.set('n', '<leader>t', builtin.git_files, {})
vim.keymap.set('n', '<leader>l', builtin.buffers, {})
