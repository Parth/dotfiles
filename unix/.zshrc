# ZSH Settings
	export PATH="/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin"
	ZSH_THEME="robbyrussell"
	export ZSH=/Users/parthmehrotra/.oh-my-zsh
	source $ZSH/oh-my-zsh.sh
	plugins=(git brew colored-man-pages cp sudo)

# Path stuff
	# For vim mappings: 
	stty -ixon

# Aliases
	alias vim="/usr/local/Cellar/vim/HEAD-9376f5f/bin/vim"
	alias v="vim"

#Functions
	# Custom cd
	c() {
		cd $1;
		ls;
	}
	alias cd="c"

# Keybindings
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

	# Paste
	function paste_to_file() {
		BUFFER="pbpaste >> $BUFFER"
		zle accept-line
	}

	zle -N paste_to_file
	bindkey "^v" paste_to_file

# SAP stuff
	source "/Applications/SQLAnywhere17/System/bin64/sa_config.sh"
	source "/Applications/SQLAnywhere17/System/bin32/sa_config.sh"

	export DYLD_LIBRARY_PATH=/Applications/SQLAnywhere17/System/lib64/:$DYLD_LIBRARY_PATH
	export DYLD_LIBRARY_PATH=/Applications/SQLAnywhere17/System/lib32/:$DYLD_LIBRARY_PATH

	# Connect to Sybase IQ on llpal57
	function connect() {
		dbisql -c "ENG=CI01;UID=pmehrotra;PWD=$1;links=tcpip(host=llbpal57.pal.sap.corp:4000)" -nogui
	}

	# Execute command on llpal57
	function execute() {
		dbisql -c "ENG=CI01;UID=pmehrotra;PWD=$1;links=tcpip(host=llbpal57.pal.sap.corp:4000)" -nogui $2
	}
