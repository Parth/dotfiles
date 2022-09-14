local nnoremap = require("mika.keymap").nnoremap
local inoremap = require("mika.keymap").inoremap

nnoremap("<leader>pv", "<cmd>Ex<Cr>")
nnoremap("<leader>b", "<cmd>ls<Cr>")
nnoremap("<leader>ls", "<cmd>ls<Cr>")

-- Telescope bindings
nnoremap("<leader>ff", "<cmd>Telescope find_files<Cr>")
nnoremap("<leader>fg", "<cmd>Telescope live_grep<Cr>")
nnoremap("<leader>fb", "<cmd>Telescope buffers<Cr>")
nnoremap("<leader>fh", "<cmd>Telescope help_tags<Cr>")

