 autoload -U colors && colors

 setopt PROMPT_SUBST

set_prompt() {
		local EXIT="$?"
	# [
	PS1="%{$fg[white]%}[%{$reset_color%}"

	# Path
	PS1+="%{$fg[cyan]%}${PWD/#$HOME/~}%{$reset_color%}"

	# Status Code
	if [[ $? -ne 0 ]]; then 
		PS1+=', '
		PS1+='%(?.%{$fg[green]%}%?.%{$fg[red]%}%?)'
	fi

	if git rev-parse --is-inside-work-tree 2> /dev/null | grep -q 'true' ; then
		PS1+=', '
		PS1+="%{$fg[blue]%}$(git rev-parse --abbrev-ref HEAD)%{$reset_color%}"
		if [ $(git status --short | wc -l) -gt 0 ]; then 
			PS1+="%{$fg[red]%}+$(git status --short | wc -l)%{$reset_color%}"
		fi
	fi


	# Timer
	if [[ $_elapsed[-1] -ne 0 ]]; then
		PS1+=', '
		PS1+="%{$fg[magenta]%}$_elapsed[-1]s%{$reset_color%}"
	fi

	# PID
	if [[ $! -ne 0 ]]; then
		PS1+=', '
		PS1+="%{$fg[yellow]%}PID:$!%{$reset_color%}"
	fi

	# Sudo
	CAN_I_RUN_SUDO=$(sudo -n uptime 2>&1|grep "load"|wc -l)
	if [ ${CAN_I_RUN_SUDO} -gt 0 ]
	then
		PS1+=', '
		PS1+="%{$fg_bold[red]%}SUDO%{$reset_color%}"
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
