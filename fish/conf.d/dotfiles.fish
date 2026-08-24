function fish_user_key_bindings
    bind -M insert ctrl-r history-pager
end

if status is-interactive
    set -g fish_key_bindings fish_vi_key_bindings
end

fish_add_path -gP $HOME/.local/bin
fish_add_path -gP $HOME/.cargo/bin
fish_add_path -gP /Applications/WezTerm.app/Contents/MacOS

set -gx EDITOR nvim
set -gx VISUAL nvim
