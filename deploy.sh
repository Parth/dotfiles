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

SOURCE=$HOME/dotfiles
PARTIAL=$HOME/.config
# BASE_CMD="stow --verbose=2 --dir=$SOURCE"
BASE_CMD="stow -v --dir=$SOURCE"

# CONFIG_DIRS=(nvim alacritty Code fish ranger vifm)
CONFIG_DIRS=(nvim alacritty vifm)

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
	deploy.sh zsh 	 - to use zshrc from dotfiles and remove from $HOME

EOF
}

function install_homedir_config {
	# zsh
	ZSHRC=$HOME/.zshrc
	[ -f "$ZSHRC" ] && rm -vf $ZSHRC
	ln --symbolic --verbose $SOURCE/zsh/zshrc.sh $HOME/.zshrc
}

function install_vim {
	if [[ ! -L "vimrc" ]]
	then
		ln --symbolic --verbose $HOME/dotfiles/vim/vimrc.vim $HOME/.vim/vimrc
	fi
	if [[ ! -L "ftplugin" ]]
	then
		ln --symbolic --verbose ~/dotfiles/vim/after/* ~/.vim/ftplugin 
	fi
	if [[ ! -L "plugin" ]]
	then
		ln --symbolic --verbose ~/dotfiles/vim/plugin/ ~/.vim
	fi
}


# MAIN
for PRG in "${CONFIG_DIRS[@]}"; do
	TARGET=$PARTIAL/$PRG
	STOW="$BASE_CMD --target=$TARGET"

	case "$1" in
		clean|unlink)
			$STOW --delete $PRG
			;;
		link)
			create_dir
			$STOW --stow $PRG
			;;
		zsh)
			install_homedir_config
			exit 0
			;;
		vim)
			install_vim
			exit 0
			;;
		*)
			usage
			exit 0
			;;
	esac
done

# END
