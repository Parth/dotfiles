#!/bin/bash

# AUTHOR      : avimehenwal
# DATE        : 25-Oct-2020
# PURPOSE     : deploy dotfiles
# FILENAME    : deploy.sh
#
# Deploy all dotfiles to corresponding configuration folders
# Folders are not created by stow
#
# DEPENDENCY: GNU Stow

SOURCE=$HOME/dotfiles/
PARTIAL=$HOME/.config/
# BASE_CMD="stow --verbose=2 --dir=$SOURCE"
BASE_CMD="stow -v --dir=$SOURCE"

# CONFIG_DIRS=(nvim alacritty Code fish ranger vifm)
CONFIG_DIRS=(nvim alacritty)

function create_dir {
	# CONFLICT when stowing alacritty: existing target is not owned by stow: alacritty.yml
	rm -rv --force $TARGET
	mkdir --parents --verbose $TARGET
}

function usage {
	toilet -f standard "avi dotfiles"
	cat << EOF
	avimehenwal dotfiles @2020

	USAGE:	deploy.sh <link|unlink>

	deploy.sh link   - to generate symlinks to config directories
	deploy.sh unlink - to remove symlinks from system config files

EOF
}

for PRG in "${CONFIG_DIRS[@]}"; do
	TARGET=$PARTIAL$PRG
	STOW="$BASE_CMD --target=$TARGET"

	case "$1" in
		clean|unlink)
			$STOW --delete $PRG
			;;
		link)
			create_dir
			$STOW --stow $PRG
			;;
		*)
			usage
			exit 0
			;;
	esac
done

# END
