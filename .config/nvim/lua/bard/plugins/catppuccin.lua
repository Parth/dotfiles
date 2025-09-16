return { 
  "catppuccin/nvim", 
  name = "catppuccin", 
  priority = 1000,
  config = function()
    require("catppuccin").setup({flavour = "macchiato"})
    vim.cmd.colorscheme "catppuccin"
    vim.cmd("hi! Normal ctermbg=NONE guibg=NONE") --opacity based on terminal
    vim.cmd("hi! Float ctermbg=NONE guibg=NONE") --opacity based on terminal
    vim.cmd("hi! NvimTreeNormal ctermbg=NONE guibg=NONE") --opacity based on terminal
  end
}
