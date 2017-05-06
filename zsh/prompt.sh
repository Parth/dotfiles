 autoload -U colors && colors

 setopt PROMPT_SUBST

set_prompt() {
	# PS1="%{$fg[red]%}%n%{$reset_color%}@%{$fg[blue]%}%m %{$fg[yellow]%}%~ %{$reset_color%}%% "
	 PS1="%{$fg[white]%}[%{$reset_color%}"
	 PS1+="%{$fg[blue]%}${PWD##*/}%{$reset_color%}"
	 PS1+="%{$fg[white]%}]: %{$reset_color%}"
	
}

set_prompt
