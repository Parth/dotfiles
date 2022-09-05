# Vars
	HISTFILE=~/.zsh_history
	SAVEHIST=10000


# Custom cd
source ~/dotfiles/zsh/plugins/fixls.zsh

chpwd() ls


autoload -U compinit && compinit

source ~/dotfiles/aliases/.aliases
source ~/dotfiles/zsh/plugins/oh-my-zsh/lib/history.zsh
source ~/dotfiles/zsh/plugins/oh-my-zsh/lib/functions.zsh
source ~/dotfiles/zsh/plugins/oh-my-zsh/lib/key-bindings.zsh
source ~/dotfiles/zsh/plugins/oh-my-zsh/lib/completion.zsh
source ~/dotfiles/zsh/plugins/oh-my-zsh/plugins/web-search/web-search.plugin.zsh
source ~/dotfiles/zsh/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh
source ~/dotfiles/zsh/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
source ~/dotfiles/zsh/prompt.sh

# Add dir colors for terminal currently doesn't suppor well for mac
if [[ "$OSTYPE" != "darwin*" ]]; then
	eval $( dircolors -b ~/dotfiles/.dir_colors )
fi

# Set default text editor to vim
export VISUAL=vim

# Utils
export PATH=$PATH:$HOME/dotfiles/utils

