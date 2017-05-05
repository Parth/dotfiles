# Aliases
	alias v="vim -p"

# Settings
	export VISUAL=vim

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
source ~/dotfiles/zsh-autosuggestions.zsh
source ~/dotfiles/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
