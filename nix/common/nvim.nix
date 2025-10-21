{ pkgs, ... }:
{
              programs.neovim = {
                enable = true;
                plugins = with pkgs.vimPlugins; [
                  nvim-web-devicons
                  telescope-nvim
                  nvim-cmp
                  cmp-nvim-lsp
                  vim-illuminate
                  lualine-nvim
                  lsp-status-nvim

                  nvim-tree-lua
                  nvim-lspconfig
                  luasnip
                  # todo replace "FabijanZulj/blame.nvim",
                ];

                extraPackages = with pkgs; [
                  lua-language-server
                  # i would like to configure this here but rustup does some wack shit
                  # rust-analyzer
                ];

                # extraLuaConfig = ''
                # 	dofile("/home/parth/dotfiles/nvim/init.lua")
                # '';
              };
}
