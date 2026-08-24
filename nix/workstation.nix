{ config, pkgs, ... }:
{
  networking.hostName = "parth-workstation-nix";

  services.xserver.videoDrivers = [ "amdgpu" ];

  hardware.graphics = {
    enable = true;
    enable32Bit = true;
    extraPackages = with pkgs; [
      rocmPackages.clr.icd
    ];
  };

  imports = [
    "/home/parth/dotfiles/nix/common.nix"
    "/home/parth/dotfiles/nix/gui.nix"
  ];

  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;
}
