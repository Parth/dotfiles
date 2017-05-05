mv ~/.zshrc ~/.zshrc.bak
mv ~/.vimrc ~/.vimrc.bak
mv ~/.tmux.conf ~/.tmux.conf.bak

sh ~/dotfiles/deploy.sh
