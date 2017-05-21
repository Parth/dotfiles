
check_for_software() {
	# command -v "$1" > /dev/null 2>&1;
	if ! [ -x "$(command -v $1)" ]; then
		echo -n "Heads up! $1 is not installed. Would you like to install it? (y/n) " >&2
		old_stty_cfg=$(stty -g)
		stty raw -echo
		answer=$( while ! head -c 1 | grep -i '[ny]' ;do true ;done )
		stty $old_stty_cfg && echo
		if echo "$answer" | grep -iq "^y" ;then
			echo "Running:	sudo pkg install $1"
			sudo pkg install $1
		fi
	else
		echo -e "$1 is installed."
	fi
}

check_for_software zsh
check_for_software vim
check_for_software tmux

echo -n "Would you like to backup your current dotfiles? (y/n) "
old_stty_cfg=$(stty -g)
stty raw -echo
answer=$( while ! head -c 1 | grep -i '[ny]' ;do true ;done )
stty $old_stty_cfg
if echo "$answer" | grep -iq "^y" ;then
	mv ~/.zshrc ~/.zshrc.old
	mv ~/.tmux.conf ~/.tmux.conf.old
	mv ~/.vimrc ~/.vimrc.old
else
	echo -e "\nNot backing up old dotfiles."
fi

printf "source '$HOME/dotfiles/zsh/zshrc_manager.sh'" > ~/.zshrc
printf "so $HOME/dotfiles/vim/vimrc.vim" > ~/.vimrc
printf "source-file $HOME/dotfiles/tmux/tmux.conf" > ~/.tmux.conf

