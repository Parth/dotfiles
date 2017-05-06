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

	PS1+="%{$fg[white]%}]: %{$reset_color%}% "
}

precmd_functions+=set_prompt
