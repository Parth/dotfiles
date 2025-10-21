{ ... }:
{
  xdg.configFile = {
    "nvim" = {
      source = /home/parth/dotfiles/nvim;
      recursive = true;
    };

    "helix" = {
      source = /home/parth/dotfiles/helix;
      recursive = true;
    };

    "aerospace" = {
      source = /home/parth/dotfiles/aerospace;
      recursive = true;
    };

    "wezterm" = {
      source = /home/parth/dotfiles/wezterm;
      recursive = true;
    };
    "sway" = {
      source = /home/parth/dotfiles/sway;
      recursive = true;
    };
  };
  home.sessionPath = [
    "$HOME/.cargo/bin"
  ];
}
