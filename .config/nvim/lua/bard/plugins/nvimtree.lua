return {
    "nvim-tree/nvim-tree.lua",
    version = "*",
    lazy = false,
    dependencies = {
      "nvim-tree/nvim-web-devicons",
    },
    config = function()
      local nvimtree = require("nvim-tree")

      nvimtree.setup({
        update_focused_file = {
          enable = true,
          update_root = true
        },
        actions = {
          open_file = {
            quit_on_open = true
          }
        }
      })

      local keymap = vim.keymap

      keymap.set('n', '<C-n>', '<cmd>NvimTreeFindFileToggle<CR>', {})
    end
}
