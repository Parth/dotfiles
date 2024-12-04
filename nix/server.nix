{
  imports = [
    "/home/parth/dotfiles/nix/common/headless.nix"
  ];

  networking.hostName = "parth-server-nix";

  # Bootloader.
  boot.loader.grub = {
    enable = true;
    device = "/dev/nvme1n1";
    useOSProber = true;
  };

  services.openssh = {
      enable = true;
      settings = {
        PermitRootLogin = "yes";
        PasswordAuthentication = true;
      };
  };

}
