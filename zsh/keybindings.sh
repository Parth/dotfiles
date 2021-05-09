# up
function up_widget() {
	BUFFER="cd .."
	zle accept-line
}
zle -N up_widget
bindkey "^k" up_widget

# Enter
function enter_line() {
	zle accept-line
}
zle -N enter_line
bindkey "^o" enter_line

# Sudo
function add_sudo() {
	BUFFER="sudo "$BUFFER
	zle end-of-line
}
zle -N add_sudo
bindkey "^s" add_sudo

# Home - Navigates to the current root workspace
function git_root() {
	BUFFER="cd $(git rev-parse --show-toplevel || echo ".")"
	zle accept-line
}
zle -N git_root
bindkey "^h" git_root
