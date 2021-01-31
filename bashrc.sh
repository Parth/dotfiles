export VISUAL=vim
export EDITOR="$VISUAL"

shopt -s checkwinsize

alias rand_console='tr -cd "[:alnum:]" < /dev/urandom | fold -w`tput cols`'

# fuzzy search in chrome history
c() {
  local cols sep google_history open
  cols=$(( COLUMNS / 3 ))
  sep='{::}'

  if [ "$(uname)" = "Darwin" ]; then
    google_history="$HOME/Library/Application Support/Google/Chrome/Default/History"
    open=open
  else
    google_history="$HOME/.config/google-chrome/Default/History"
    open=xdg-open
  fi
  cp -f "$google_history" /tmp/h
  sqlite3 -separator $sep /tmp/h \
    "select substr(title, 1, $cols), url
     from urls order by last_visit_time desc" |
  awk -F $sep '{printf "%-'$cols's  \x1b[36m%s\x1b[m\n", $1, $2}' |
  fzf --ansi --multi | sed 's#.*\(https*://\)#\1#' | xargs $open > /dev/null 2> /dev/null
}

man-find() {
    f=$(fd . $MANPATH/man${1:-1} -t f -x echo {/.} | fzf) && man $f
}
fman() {
    man -k . | fzf --prompt='Man> ' | awk '{print $1}' | xargs -r man
}

# don't put duplicate lines or lines starting with space in the history.
# See bash(1) for more options
HISTCONTROL=ignoreboth

# append to the history file, don't overwrite it
shopt -s histappend

# for setting history length see HISTSIZE and HISTFILESIZE in bash(1)
HISTSIZE=1000
HISTFILESIZE=2000

# check the window size after each command and, if necessary,
# update the values of LINES and COLUMNS.
shopt -s checkwinsize

# Add an "alert" alias for long running commands.  Use like so:
#   sleep 10; alert
alias alert='notify-send --urgency=low -i "$([ $? = 0 ] && echo terminal || echo error)" "$(history|tail -n1|sed -e '\''s/^\s*[0-9]\+\s*//;s/[;&|]\s*alert$//'\'')"'

# vim smali syntax
echo au BufRead,BufNewFile *.smali set filetype=smali >> ~/.vim/filetype.vim
 && mkdir ~/.vim/syntax && cd $_ && wget http://codetastrophe.com/smali.vim

alias switch_proxy='sudo systemctl reload tor.service && curl -s -x socks5h://localhost:9050 ifconfig.me && echo'

# Disable Ctrl+S (Pause) and Ctrl+Q (continue) shortcuts, I use Ctrl+S to save inside Vim
stty -ixon 

