{ pkgs, lib, ... }: {
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

  systemd.services."getty@tty1".enable = false;

  services.github-runners.lockbook = {
    enable = true;
    name = "lockbook ci";
    user = "parth";
    extraLabels = [ "ci" ];
    tokenFile = "/home/parth/token";
    url = "https://github.com/lockbook/lockbook";
    extraPackages = with pkgs; [
      rustup
      gcc
      libxkbcommon
    ];
    serviceOverrides = {
      ProtectSystem = "no";
      ProtectHome = "no";
      PrivateTmp = false;
      PrivateDevices = false;
    };
    extraEnvironment = {
      NIX_PATH = "/nix/var/nix/profiles/per-user/root/channels/nixos";
    };
  };
}
