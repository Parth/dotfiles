{ pkgs, lib, ... }: {


  # from: https://wiki.nixos.org/wiki/Sway
  environment.systemPackages = with pkgs; [
    grim
    slurp
    wl-clipboard
    mako
    wdisplays
  ];
  services.gnome.gnome-keyring.enable = true;
  programs.sway = {
    enable = true;
    wrapperFeatures.gtk = true;
  };
  xdg.portal = {
    enable = true;
    wlr.enable = true;
    extraPortals = [ pkgs.xdg-desktop-portal-gtk ];
  };
  # end sway

  services.printing.enable = true;
  services.pulseaudio.enable = false;
  security.rtkit.enable = true;
  services.pipewire = {
    enable = true;
    alsa.enable = true;
    alsa.support32Bit = true;
    pulse.enable = true;
  };

  fonts.packages = [ ] ++ builtins.filter lib.attrsets.isDerivation (builtins.attrValues pkgs.nerd-fonts);

  users.users.parth.packages = with pkgs; [
    zed-editor
    _1password-gui
    google-chrome
    discord
    spotify
    wezterm
    lockbook-desktop
    nautilus
    vlc
  ];

  programs.obs-studio = {
    enable = true;
    plugins = with pkgs.obs-studio-plugins; [
      obs-vaapi #optional AMD hardware acceleration
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
