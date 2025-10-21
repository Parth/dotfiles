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
    interactiveShellInit = ''
         	fish_vi_key_bindings
          set -gx PATH $HOME/.cargo/bin $PATH
          set -gx EDITOR nvim
          set -gx VISUAL nvim
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
      lfs.enable = true;
      extraConfig = {
        push.default = "current";
      };
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
        render-markdown-nvim
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



    xdg.configFile = {
      "nvim" = {
        source = /home/parth/dotfiles/nvim;
        recursive = true;
      };

      "helix" = {
        source = /home/parth/dotfiles/helix;
        recursive = true;
      };

      "aerospace" = {
        source = /home/parth/dotfiles/aerospace;
        recursive = true;
      };

      "wezterm" = {
        source = /home/parth/dotfiles/wezterm;
        recursive = true;
      };
      "sway" = {
        source = /home/parth/dotfiles/sway;
        recursive = true;
      };
    };
    home.sessionPath = [
      "$HOME/.cargo/bin"
    ];
  };

  users.users.parth = {
    isNormalUser = true;
    description = "parth";
    extraGroups = [ "networkmanager" "wheel" ];
    packages = with pkgs; [
      zola

      helix

      fzf
      eza
      xclip

      ripgrep
      clang

      samba

      rust-analyzer
      rustup
      nixd
      lua-language-server
      nixpkgs-fmt

      google-cloud-sdk
      lockbook

      git-lfs
    ];
  };

  environment.variables = { EDITOR = "nvim"; VISUAL = "nvim"; };

  programs.git.enable = true;
  nixpkgs.config.allowUnfree = true;
  system.stateVersion = "24.05";

    fileSystems."/truenas" = {
      device = "//192.168.12.2/parth-dataset";
      fsType = "cifs";
      options = [
        "credentials=/etc/nixos/smb-secrets"
        "uid=1000"
        "gid=100"
        "vers=3.0"
        "x-systemd.automount"
        "noauto"
      ];
    };

}
