# up
	function up_widget() {
		BUFFER="cd ..;"
		zle accept-line
	}
	zle -N up_widget
	bindkey "^k" up_widget

# git
	function git_prepare() {
		if [ -n "$BUFFER" ];
			then
				BUFFER="git add -A; git commit -m \"$BUFFER\" && git push"
		fi

		if [ -z "$BUFFER" ];
			then
				BUFFER="git add -A; git commit -m \"quick change\" && git push"
		fi
				
		zle accept-line
	}
	zle -N git_prepare
	bindkey "^g" git_prepare

# compile and run
	#TODO 
	function re_run() {
		BUFFER="!!"
		zle accept-line
	}
	zle -N re_run
	bindkey "^r" re_run
