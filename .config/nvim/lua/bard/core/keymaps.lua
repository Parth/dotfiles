vim.g.mapleader = " "

local keymap = vim.keymap

-- Colemak hjkl
vim.cmd("noremap j h")
vim.cmd("noremap h k")
vim.cmd("noremap k j")

keymap.set("n", "<leader>tj", "<cmd>tabp<CR>", { desc = "Go to previous tab" })
keymap.set("n", "<leader>tl", "<cmd>tabn<CR>", { desc = "Go to next tab" })
keymap.set("n", "<leader>tx", "<cmd>tabclose<CR>", { desc = "Close current tab" })

keymap.set("x", "<leader>p", "\"_dP", { desc = "past over selection without losing copied text" })

vim.keymap.set("n", "<leader>s", [[:%s/\<<C-r><C-w>\>/<C-r><C-w>/gI<Left><Left><Left>]], { desc = "replace word cursor is on" })

