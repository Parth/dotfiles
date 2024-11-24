# Edit this configuration file to define what should be installed on
# your system.  Help is available in the configuration.nix(5) man page
# and in the NixOS manual (accessible by running ‘nixos-help’).

{ config, pkgs, ... }:

let
  home-manager = builtins.fetchTarball "https://github.com/nix-community/home-manager/archive/release-24.05.tar.gz";
in
{
  imports =
    [
      # Include the results of the hardware scan.
      ./hardware-configuration.nix
      (import "${home-manager}/nixos")
    ];

  # Bootloader.
  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;

  networking.hostName = "nixos"; # Define your hostname.
  # networking.wireless.enable = true;  # Enables wireless support via wpa_supplicant.

  networking.networkmanager.enable = true;

  # Set your time zone.
  time.timeZone = "America/New_York";

  # Select internationalisation properties.
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
  };


  services.xserver.enable = true;

  services.xserver.displayManager.gdm.enable = true;
  services.xserver.desktopManager.gnome.enable = true;

  services.xserver.xkb = {
    layout = "us";
    variant = "";
  };

  services.printing.enable = true;

  hardware.pulseaudio.enable = false;
  security.rtkit.enable = true;
  services.pipewire = {
    enable = true;
    alsa.enable = true;
    alsa.support32Bit = true;
    pulse.enable = true;
  };

  users.users.parth = {
    isNormalUser = true;
    description = "parth";
    extraGroups = [ "networkmanager" "wheel" ];
    packages = with pkgs; [
      fzf
      ripgrep
      clang

      rust-analyzer
      rustup

      nixd
    ];
  };

  services.xserver.displayManager.autoLogin.enable = true;
  services.xserver.displayManager.autoLogin.user = "parth";

  systemd.services."getty@tty1".enable = false;
  systemd.services."autovt@tty1".enable = false;

  programs.firefox.enable = true;
  programs.git.enable = true;

  nixpkgs.config.allowUnfree = true;

  environment.systemPackages = with pkgs; [
    xclip
  ];

  system.stateVersion = "24.05";
}
