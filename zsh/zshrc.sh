# Vars
HISTFILE=~/.zsh_history
SAVEHIST=10000


# Custom cd
source ~/dotfiles/zsh/plugins/fixls.zsh

chpwd() ls

# a411ef3

autoload -U compinit && compinit

source ~/dotfiles/aliases/.aliases

source ~/dotfiles/zsh/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh
source ~/dotfiles/zsh/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
source ~/dotfiles/zsh/prompt.sh
source ~/dotfiles/zsh/keybindings.sh
source ~/dotfiles/zsh/bindings.zsh
source ~/dotfiles/zsh/history.zsh


# Add dir colors for terminal currently doesn't suppor well for mac
if [[ "$OSTYPE" != "darwin"* ]]; then
	eval $( dircolors -b ~/dotfiles/.dir_colors )
fi

# Set default text editor to vim
export VISUAL=nvim