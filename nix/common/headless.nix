{ pkgs, ... }:

let
  home-manager = builtins.fetchTarball "https://github.com/nix-community/home-manager/archive/release-25.05.tar.gz";
in
{
  imports =
    [
      # Include the results of the hardware scan.
      # ./hardware-configuration.nix
      "/etc/nixos/hardware-configuration.nix"
      "/home/parth/dotfiles/nix/common/fish.nix"
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

  users.defaultUserShell = pkgs.fish;

  home-manager.users.parth = {
    /* The home.stateVersion option does not have a default and must be set */
    home.stateVersion = "18.09";
    /* Here goes the rest of your home-manager config, e.g. home.packages = [ pkgs.foo ]; */

    imports = [
      "/home/parth/dotfiles/nix/common/nvim.nix"
      "/home/parth/dotfiles/nix/common/git.nix"
      "/home/parth/dotfiles/nix/common/xdg.nix"
    ];
  };

  users.users.parth = {
    isNormalUser = true;
    description = "parth";
    extraGroups = [ "networkmanager" "wheel" ];
    packages = with pkgs; [
      fzf
      ripgrep
      clang
      samba
      rust-analyzer
      rustup
      nixpkgs-fmt
      google-cloud-sdk
      lockbook
    ];
  };

  environment.variables = { EDITOR = "nvim"; VISUAL = "nvim"; };
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
