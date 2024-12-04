{ pkgs, ... }: {

  services.xserver.enable = true;
  services.xserver.displayManager.gdm.wayland = false;
  services.xserver.displayManager.gdm.enable = true;
  services.xserver.desktopManager.gnome.enable = true;
  services.xserver.displayManager.autoLogin.enable = true;
  services.xserver.displayManager.autoLogin.user = "parth";

  services.xserver.xkb = {
    layout = "us";
    variant = "";
  };

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
    slack
  ];

  programs._1password-gui.enable = true;
  programs.chromium = {
    enable = true;
    extraOpts = {
      "PasswordManagerEnabled" = false;
    };
  };

}
