#!/bin/sh

if [ $# -eq 0 ]
  then
    echo "supply <machine.nix> file as argument"
    exit 1
fi

sudo rm -rf /etc/nixos/configuration.nix && sudo cp $HOME/dotfiles/nix/$1 /etc/nixos/configuration.nix && sudo nixos-rebuild switch
