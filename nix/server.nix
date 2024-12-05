{ pkgs, ... }: {
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
      ci-env
      #       pkg-config
      #       gtk3
      #       glib
      #       gobject-introspection
      #       gdk-pixbuf
    ];
    serviceOverrides = {
      ProtectSystem = "no";
      ProtectHome = "no";
      PrivateTmp = false;
      PrivateDevices = false;
    };
    #     extraEnvironment = {
    #       PKG_CONFIG_PATH = "${pkgs.gtk3.dev}/lib/pkgconfig:${pkgs.glib.dev}/lib/pkgconfig:${pkgs.gobject-introspection.dev}/lib/pkgconfig:${pkgs.gdk-pixbuf.dev}/lib/pkgconfig:${pkgs.atk.dev}/lib/pkgconfig";
    #     };
  };

  environment.systemPackages = with pkgs; [
    (buildEnv {
      name = "ci-env";
      paths = [
        pkg-config
        gtk3
        glib
        gobject-introspection
        gdk-pixbuf
        atk
      ];
    })
  ];
}
