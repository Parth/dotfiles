 autoload -U colors && colors

 setopt PROMPT_SUBST

set_prompt() {
    	local EXIT="$?"
	# [
	PS1="%{$fg[white]%}[%{$reset_color%}"

	# Path
	PS1+="%{$fg[cyan]%}${PWD/#$HOME/~}%{$reset_color%}"

	# Status Code
	PS1+=', '
	PS1+='%(?.%{$fg[green]%}%?.%{$fg[red]%}%?)'

	if [[ $(git rev-parse --is-inside-work-tree) == "true" ]]; then
		PS1+=', '
		PS1+="%{$fg[blue]%}$(git branch)%{$reset_color%}"
	fi


	# Timer
	if [[ $_elapsed[-1] -ne 0 ]]; then
		PS1+=', '
		PS1+="%{$fg[blue]%}$_elapsed[-1]s%{$reset_color%}"
	fi

	PS1+="%{$fg[white]%}]: %{$reset_color%}% "
}

precmd_functions+=set_prompt

preexec () {
   (( ${#_elapsed[@]} > 1000 )) && _elapsed=(${_elapsed[@]: -1000})
   _start=$SECONDS
}

precmd () {
   (( _start >= 0 )) && _elapsed+=($(( SECONDS-_start )))
   _start=-1 
}
