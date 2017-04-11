# Aliases
	alias v="vim"

#Functions
	# Custom cd
	c() {
		cd $1;
		ls;
	}
	alias cd="c"

# For vim mappings: 
	stty -ixon

source ~/dotfiles/keybindings.sh
source ~/dotfiles/zsh-autosuggestions/zsh-autosuggestions.zsh
