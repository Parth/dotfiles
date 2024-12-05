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

      pkg-config
      gtk3
      glib
      gobject-introspection
      gdk-pixbuf
    ];
    serviceOverrides = {
      ProtectSystem = "no";
      ProtectHome = "no";
      PrivateTmp = false;
      PrivateDevices = false;
    };
    extraEnvironment = {
      PKG_CONFIG_PATH = lib.makeSearchPath "pkgconfig" [
        pkgs.gtk3.dev
        pkgs.at-spi2-core.dev
        pkgs.dbus.dev
        pkgs.expat.dev
        pkgs.glib.dev
        pkgs.zlib.dev
        pkgs.libffi.dev
        pkgs.cairo.dev
        pkgs.fontconfig.dev
        pkgs.freetype.dev
        pkgs.bzip2.dev
        pkgs.brotli.dev
        pkgs.libpng-apng.dev
        pkgs.pixman
        pkgs.libXext.dev
        pkgs.xorgproto
        pkgs.libXau.dev
        pkgs.libXrender.dev
        pkgs.libX11.dev
        pkgs.libxcb.dev
        pkgs.fribidi.dev
        pkgs.gdk-pixbuf.dev
        pkgs.libtiff.dev
        pkgs.libdeflate
        pkgs.libjpeg-turbo.dev
        pkgs.xz.dev
        pkgs.gsettings-desktop-schemas
        pkgs.libICE.dev
        pkgs.libSM.dev
        pkgs.libXcomposite.dev
        pkgs.libXfixes.dev
        pkgs.libXcursor.dev
        pkgs.libXdamage.dev
        pkgs.libXi.dev
        pkgs.libXrandr.dev
        pkgs.pango.dev
        pkgs.harfbuzz.dev
        pkgs.graphite2.dev
        pkgs.libXft.dev
        pkgs.libGL.dev
        pkgs.libglvnd.dev
        pkgs.wayland.dev
        pkgs.wayland.bin
        pkgs.wayland-protocols
        pkgs.libXinerama.dev
        pkgs.cups.dev
        pkgs.gmp.dev
        pkgs.gobject-introspection-wrapped.dev
        pkgs.gobject-introspection.dev
      ];
      # PKG_CONFIG_PATH = "${pkgs.gtk3.dev}/lib/pkgconfig:${pkgs.glib.dev}/lib/pkgconfig:${pkgs.gobject-introspection.dev}/lib/pkgconfig:${pkgs.gdk-pixbuf.dev}/lib/pkgconfig:${pkgs.atk.dev}/lib/pkgconfig";
    };
  };

  # environment.systemPackages = with pkgs; [
  #   (buildEnv {
  #     name = "ci-env";
  #     paths = [
  #       pkg-config
  #       gtk3
  #       glib
  #       gobject-introspection
  #       gdk-pixbuf
  #       atk
  #     ];
  #   })
  # ];
}
