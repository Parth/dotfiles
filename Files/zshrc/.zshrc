export ZSH=/Users/parthmehrotra/.oh-my-zsh
ZSH_THEME="robbyrussell"
plugins=(git brew colored-man-pages cp tmux sudo)
ZSH_TMUX_AUTOSTART=false
export PATH="/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin"
source $ZSH/oh-my-zsh.sh
alias zshrc="vim ~/.zshrc"
alias gall="ga -A; gc && gp"
alias gac="ga -A; gc"
alias lr="ls -AR"
alias v="vim"
alias copy="pwd | pbcopy"

# The next line updates PATH for the Google Cloud SDK.
source '/Users/parthmehrotra/google-cloud-sdk/path.zsh.inc'

# The next line enables shell command completion for gcloud.
source '/Users/parthmehrotra/google-cloud-sdk/completion.zsh.inc'
source "/Users/parthmehrotra/google-cloud-sdk/path.zsh.inc"
source "/Users/parthmehrotra/google-cloud-sdk/completion.zsh.inc"

# For latex
export PATH=$PATH:/Library/TeX/Distributions/.DefaultTeX/Contents/Programs/texbin

# How I usually search for things
search() {
	grep -R $1 .
}
