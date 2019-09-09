# up
	function up_widget() {
		BUFFER="cd .."
		zle accept-line
	}
	zle -N up_widget
	bindkey "^k" up_widget

# git
	function git_prepare() {
		if [ -n "$BUFFER" ];
			then
				BUFFER="git add . && git commit -m \"$BUFFER\""
		fi

		if [ -z "$BUFFER" ];
			then
				BUFFER="git add . && git commit -v"
		fi
				
		zle accept-line
	}
	zle -N git_prepare
	bindkey "^g" git_prepare

    function git_push() {
        BUFFER="git push"
		zle accept-line
    }
	zle -N git_push
	bindkey "^p" git_push

# home
	function goto_home() { 
		BUFFER="cd ~/"$BUFFER
		zle end-of-line
		zle accept-line
	}
	zle -N goto_home
	bindkey "^h" goto_home

# LS
	function ctrl_l() {
		BUFFER="ls"
		zle accept-line
	}
	zle -N ctrl_l
	bindkey "^l" ctrl_l

# Clear
	function ctrl_j() {
		BUFFER="clear"
		zle accept-line
	}
	zle -N ctrl_j
	bindkey "^j" ctrl_j


# Sudo
	function add_sudo() {
		BUFFER="sudo "$BUFFER
		zle end-of-line
	}
	zle -N add_sudo
	bindkey "^s" add_sudo
