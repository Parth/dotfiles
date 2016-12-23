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
	function compile_and_run() {
		BUFFER="./compile.sh && ./run.sh"
		zle accept-line
	}
	zle -N compile_and_run
	bindkey "^r" compile_and_run
