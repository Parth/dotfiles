#!/bin/sh

rm -rf /etc/nix-darwin/flake.nix && cp $HOME/dotfiles/nix/macbook.nix /etc/nix-darwin/flake.nix && sudo nix run nix-darwin/master#darwin-rebuild -- switch
