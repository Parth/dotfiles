{ pkgs, ... }: {


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
  # end sway

  services.printing.enable = true;
  hardware.pulseaudio.enable = false;
  security.rtkit.enable = true;
  services.pipewire = {
    enable = true;
    alsa.enable = true;
    alsa.support32Bit = true;
    pulse.enable = true;
  };

  fonts.packages = with pkgs; [
    nerdfonts
  ];

  users.users.parth.packages = with pkgs; [
    _1password-gui
    google-chrome
    discord
    spotify
    wezterm
    lockbook-desktop
  ];

  programs._1password-gui.enable = true;
  programs.chromium = {
    enable = true;
    extraOpts = {
      "PasswordManagerEnabled" = false;
    };
  };

  systemd.services."getty@tty1".enable = false;
  systemd.services."autovt@tty1".enable = false;
}
