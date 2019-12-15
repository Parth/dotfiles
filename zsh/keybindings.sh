# git
	function git_prepare() {
		if [ -n "$BUFFER" ];
			then
				BUFFER="git add . && git commit -m \"$BUFFER\" && git push"
		fi

		if [ -z "$BUFFER" ];
			then
				BUFFER="git add . && git commit -v && git push"
		fi
				
		zle accept-line
	}
	zle -N git_prepare
	bindkey "^g" git_prepare

# Edit and rerun
	function edit_and_run() {
		BUFFER="fc"
		zle accept-line
	}
	zle -N edit_and_run
	bindkey "^b" edit_and_run

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
