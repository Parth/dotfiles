-- This file can be loaded by calling `lua require('plugins')` from your init.vim

-- Only required if you have packer configured as `opt`
vim.cmd [[packadd packer.nvim]]

return require('packer').startup(function(use)
  -- Packer can manage itself
  use 'wbthomason/packer.nvim'
  use 'folke/tokyonight.nvim'
  use {'neoclide/coc.nvim', branch='release'}
  use {'nvim-telescope/telescope.nvim', tag = '0.1.0',
      -- or                            , branch = '0.1.x',
       requires = { {'nvim-lua/plenary.nvim'} } }
  use 'github/copilot.vim'
  -- For some reason Packer can't resolve the username or something... So I ran this instead
  -- git clone https://github.com/fatih/vim-go.git ~/.local/share/nvim/site/pack/plugins/start/vim-go
  -- use 'fatih/vim-go.nvim'
end)

