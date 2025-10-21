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
      # vim-sleuth
      # todo replace "FabijanZulj/blame.nvim",
    ];

    extraPackages = with pkgs; [
      lua-language-server
      nil
      nixd
    ];
  };
}
