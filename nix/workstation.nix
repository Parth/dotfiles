{ config, ... }:
{
  networking.hostName = "parth-workstation-nix";

  services.xserver.videoDrivers = [ "amdgpu" ];

  # Load nvidia driver for Xorg and Wayland
  hardware.graphics = {
    enable = true;
    enable32Bit = true;
  };

  imports = [
    "/home/parth/dotfiles/nix/common/headless.nix"
    "/home/parth/dotfiles/nix/common/gui.nix"
  ];

  # Bootloader.
  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;
}
