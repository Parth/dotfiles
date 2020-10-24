#!/bin/bash

# AUTHOR      : avimehenwal
# DATE        : 21-Oct-2020
# PURPOSE     : configure Plug
# FILENAME    : configure.sh
#
# Install Plug vim plugin manager
# https://github.com/junegunn/vim-plug

function update_vim_plug {
  curl -fLo ~/.vim/autoload/plug.vim --create-dirs \
    https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
}

function install_neovim_vim_plug {
  sh -c 'curl -fLo "${XDG_DATA_HOME:-$HOME/.local/share}"/nvim/site/autoload/plug.vim --create-dirs \
       https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim'
}

function install_minpack {
  git clone https://github.com/k-takata/minpac.git ~/.vim/pack/minpac/opt/minpac
}

function isPlug_installed {
  if [ ! -f ~/.vim/autoload/plug.vim ]
  then
    update_vim_plug
  else
    echo "vim-Plug already installed"
  fi
}

function install_neovim {
  sudo apt install neovim
  sudo apt install python-neovim
  sudo apt install python3-neovim
}

# MAIN
# update_vim_plug
# isPlug_installed
# install_minpack
install_neovim_vim_plug

# END