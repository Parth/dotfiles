{
  imports = [
    "/home/parth/dotfiles/nix/common.nix"
    "/home/parth/dotfiles/nix/gui.nix"
  ];

  networking.hostName = "parth-laptop-nix";

  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;
}
