{
  imports = [
    "/home/parth/dotfiles/nix/common/headless.nix"
    "/home/parth/dotfiles/nix/common/gui.nix"
  ];

  networking.hostName = "parth-laptop-nix";

  # Bootloader.
  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;
}
