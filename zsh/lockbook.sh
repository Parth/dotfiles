export LOCKBOOK_EDITOR="vim"

alias all="lockbook list-all | fzf --prompt='Select a file: '"
alias dirs="lockbook list-folders | fzf --prompt='Select a folder: '"
alias docs="lockbook list-docs | grep -v 'parth/trash' | fzf --prompt='Select a document: '"
alias edit='lockbook edit $(docs)'

function new_document() {
	BUFFER='lockbook new $(dirs)'
	zle end-of-line
	BUFFER='lockbook new $(dirs) && lockbook sync'
}

zle -N new_document
bindkey "^l" new_document

function edit_document() {
	BUFFER='lockbook edit $(docs) && lockbook sync'
	zle accept-line
}
zle -N edit_document
bindkey "^f" edit_document

alias configure="vim ~/dotfiles/zsh/lockbook.sh"
