 autoload -U colors && colors

 setopt PROMPT_SUBST

set_prompt() {
    	local EXIT="$?"
	# [
	PS1="%{$fg[white]%}[%{$reset_color%}"

	# Path
	PS1+="%{$fg[blue]%}${PWD/#$HOME/~}%{$reset_color%}"

	# Status Code
	PS1+=', '
	PS1+='%(?.%{$fg[green]%}%?.%{$fg[red]%}%?)'

#	# Status Code: Credit [http://stackoverflow.com/questions/16715103/bash-prompt-with-last-exit-code]
#	PS1+=", "
#	local EXIT="$?"
#	if [$EXIT != 0]; then
#	else
#		PS1+="%{$fg[green]%} ${PWD##*/} %{$reset_color%}"
#	fi
#
#	# ]
	PS1+="%{$fg[white]%}]: %{$reset_color%}% "
}

set_prompt
