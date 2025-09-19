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
      PasswordAuthentication = false;
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
      psmisc
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
      LIBRARY_PATH = "${pkgs.libxkbcommon}/lib";
    };
  };

  users.users.parth = {
    openssh.authorizedKeys.keys = [
      "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDMjLtM4DKvdCdgajSHcEwFsG2DSdgJ4I4IB4t53YhW8j9iwzmh4wSGQ/lpEiXenfByoeDT6m5idVqMVzTaQScMxKoo+CMcu3gQhj1lK+QKbdCGtXZe6fI8KAJklJxLL11FB8dh3C7LNqI7IQJQD6b2YBqnT1sNlXloNu/ZtOvrt4nOBNrubAipXnTBJDp77ZJfLEv+mlG7cgLWBpTlHTIL5iFfr4sm3hQwqK393FGamVFm6IefEdI8kYXtTHo1WX35XCAgblGjyAk/ic6Xp1va/l6NQRvdYJVaCeI93xWQQ0xuOj7WoicVF6sKrg5HRMYR/YLFLUonSkZeNEXkkgWSpQdwIiYllz4DqFtMnZ6iZKpg4ZmVXFikG2eifCub48YQL31mwGzmpDMfdHjP92CyjgOsJtG23uyEX6RA+3XLrkoSowFql2FwKGV+bQ5ymfzIIwdS8FSZootgDP+KVFG1CJhffcHdQ8TosBqjqZ/NkNhvee1jwbCO/uR4Qv5yxL0="
    ];
  };

  users.users.adam = {
    isNormalUser = true;
    home = "/home/adam";
    description = "Adam's account";
    extraGroups = [ "wheel" "networkmanager" ];
    openssh.authorizedKeys.keys = [
      "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBLMux74pTJaMlfX/sqBnggtRjwoIMgp2Glg6puQZxgC aew31gcmuy@gmail.com"
    ];
  };
}


