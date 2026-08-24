{ pkgs, lib, ... }: {

  programs.sway = {
    enable = true;
    wrapperFeatures.gtk = true;
  };
  xdg.portal = {
    enable = true;
    wlr.enable = true;
    extraPortals = [ pkgs.xdg-desktop-portal-gtk ];
  };
  services.gnome.gnome-keyring.enable = true;

  environment.systemPackages = with pkgs; [
    swaylock
    swaybg
    wmenu
    brightnessctl
    grim
    slurp
    wl-clipboard
    mako
    wdisplays
  ];

  services.printing.enable = true;
  services.flatpak.enable = true;
  services.pulseaudio.enable = false;
  security.rtkit.enable = true;
  services.pipewire = {
    enable = true;
    alsa.enable = true;
    alsa.support32Bit = true;
    pulse.enable = true;
  };

  fonts.packages = builtins.filter lib.attrsets.isDerivation (builtins.attrValues pkgs.nerd-fonts);

  users.users.parth.packages = with pkgs; [
    wezterm
    google-chrome
    _1password-gui
    discord
    spotify
    zed-editor
    lockbook
    lockbook-desktop
    nautilus
    vlc
    davinci-resolve-studio
  ];

  programs.obs-studio = {
    enable = true;
    plugins = with pkgs.obs-studio-plugins; [
      obs-vaapi
    ];
  };

  programs._1password-gui.enable = true;
  programs.chromium = {
    enable = true;
    extraOpts = {
      "PasswordManagerEnabled" = false;
    };
  };

  systemd.services."getty@tty1".enable = false;
  systemd.services."autovt@tty1".enable = false;

  programs.virt-manager.enable = true;
  users.groups.libvirtd.members = [ "parth" ];
  virtualisation.libvirtd.enable = true;
  virtualisation.spiceUSBRedirection.enable = true;
}
