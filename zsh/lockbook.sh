export LOCKBOOK_EDITOR="vim"

alias lls="lockbook list | fzf"
alias lvim="lockbook list | fzf | lockbook edit"
alias lcat="lockbook list | fzf | lockbook print"
alias lrm="lockbook list | fzf | lockbook remove"

alias configure="vim ~/dotfiles/zsh/lockbook.sh"
