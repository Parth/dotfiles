export LOCKBOOK_EDITOR="vim"

alias lls="lockbook list | fzf"
alias lvim="lockbook list-docs | fzf | lockbook edit && lockbook sync"
alias lcat="lockbook list | fzf | lockbook print"

alias configure="vim ~/dotfiles/zsh/lockbook.sh"
