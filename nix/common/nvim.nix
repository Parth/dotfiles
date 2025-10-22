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

      nvim-tree-lua
      nvim-lspconfig
      luasnip
      vim-sleuth
      nvim-treesitter
      nvim-treesitter.withAllGrammars
      gitsigns-nvim
      fidget-nvim
    ];

    extraPackages = with pkgs; [
      lua-language-server
      nil
      nixd
    ];
  };
}
