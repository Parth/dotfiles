{ pkgs, lib, ... }:

let
  home-manager = builtins.fetchTarball "https://github.com/nix-community/home-manager/archive/release-24.05.tar.gz";
in
{
  imports =
    [
      # Include the results of the hardware scan.
      # ./hardware-configuration.nix
      "/etc/nixos/hardware-configuration.nix"
      (import "${home-manager}/nixos")
    ];

  networking.networkmanager.enable = true;

  time.timeZone = "America/New_York";
  i18n.defaultLocale = "en_US.UTF-8";
  i18n.extraLocaleSettings = {
    LC_ADDRESS = "en_US.UTF-8";
    LC_IDENTIFICATION = "en_US.UTF-8";
    LC_MEASUREMENT = "en_US.UTF-8";
    LC_MONETARY = "en_US.UTF-8";
    LC_NAME = "en_US.UTF-8";
    LC_NUMERIC = "en_US.UTF-8";
    LC_PAPER = "en_US.UTF-8";
    LC_TELEPHONE = "en_US.UTF-8";
    LC_TIME = "en_US.UTF-8";
  };

  programs.fish = {
    enable = true;
    shellInit = ''
      		fish_vi_key_bindings
      	'';
  };
  users.defaultUserShell = pkgs.fish;

  home-manager.users.parth = {
    /* The home.stateVersion option does not have a default and must be set */
    home.stateVersion = "18.09";
    /* Here goes the rest of your home-manager config, e.g. home.packages = [ pkgs.foo ]; */
    programs.git = {
      enable = true;
      userName = "parth";
      userEmail = "parth@mehrotra.me";
    };


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
        nixpkgs-fmt
        lua-language-server
        # i would like to configure this here but rustup does some wack shit
        # rust-analyzer
      ];

      # extraLuaConfig = ''
      # 	dofile("/home/parth/dotfiles/nvim/init.lua")
      # '';
    };



    xdg.configFile = {
      "nvim" = {
        source = /home/parth/dotfiles/nvim;
        recursive = true;
      };
    };

    home.activation.cloneLockbook = lib.mkAfter ''
      #!/usr/bin/env bash

      if [ ! -d $HOME/Documents/lockbook/lockbook ]; then
          mkdir -p $HOME/Documents/lockbook/;
          cd $HOME/Documents/lockbook && git clone git@github.com:lockbook/lockbook.git
      fi

      if [ ! -d $HOME/Documents/lockbook/nixpkgs ]; then
          mkdir -p $HOME/Documents/lockbook/;
          cd $HOME/Documents/lockbook && git clone git@github.com:lockbook/nixpkgs.git
      fi

      if [ ! -d $HOME/Documents/lockbook/db-rs ]; then
          mkdir -p $HOME/Documents/lockbook/;
          cd $HOME/Documents/lockbook && git clone git@github.com:lockbook/db-rs.git
      fi

      if [ ! -d $HOME/Documents/lockbook/cli-rs ]; then
          mkdir -p $HOME/Documents/lockbook/;
          cd $HOME/Documents/lockbook && git clone git@github.com:lockbook/cli-rs.git
      fi
    '';
  };

  users.users.parth = {
    isNormalUser = true;
    description = "parth";
    extraGroups = [ "networkmanager" "wheel" ];
    packages = with pkgs; [
      fzf
      xclip

      ripgrep
      clang

      samba

      # move these to neovim specific area 
      rust-analyzer
      rustup

      nixd
    ];
  };



  programs.git.enable = true;

  nixpkgs.config.allowUnfree = true;

  system.stateVersion = "24.05";
}
