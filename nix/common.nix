{ pkgs, ... }:
{
  imports = [ "/etc/nixos/hardware-configuration.nix" ];

  networking.networkmanager.enable = true;
  time.timeZone = "America/New_York";
  i18n.defaultLocale = "en_US.UTF-8";
  nixpkgs.config.allowUnfree = true;
  system.stateVersion = "24.05";

  users.users.parth = {
    isNormalUser = true;
    description = "parth";
    extraGroups = [ "networkmanager" "wheel" ];
  };

  environment.systemPackages = with pkgs; [
    git
    curl
    xz
    gcc
  ];

  programs.nix-ld = {
    enable = true;
    libraries = with pkgs; [
      stdenv.cc.cc.lib
      zlib
    ];
  };

  environment.shells = [ "/home/parth/.local/bin/fish" ];

  environment.variables = {
    EDITOR = "nvim";
    VISUAL = "nvim";
  };

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
