mv ~/.zshrc ~/.zshrc.old
mv ~/.tmux.conf ~/.tmux.conf.old
mv ~/.vimrc ~/.vimrc.old

printf "source '$HOME/dotfiles/zsh/zshrc_manager.sh'" > ~/.zshrc
printf "so $HOME/dotfiles/vim/vimrc.vim" > ~/.vimrc
printf "source-file $HOME/dotfiles/tmux/tmux.conf" > ~/.tmux.conf

