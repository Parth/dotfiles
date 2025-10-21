{ ... }:
{
  programs.fish = {
    enable = true;
    interactiveShellInit = ''
        fish_vi_key_bindings
        set -gx PATH $HOME/.cargo/bin $PATH
        set -gx EDITOR nvim
        set -gx VISUAL nvim
      	'';
  };
}
