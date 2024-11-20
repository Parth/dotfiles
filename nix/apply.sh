#!/bin/sh

sudo rm -rf /etc/nixos/configuration.nix && sudo cp $HOME/dotfiles/nix/configuration.nix /etc/nixos/ &&  sudo nixos-rebuild switch
