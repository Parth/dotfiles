echo "Updating rc files"
(cd ~/dotfiles && timeout 2 git pull)
source ~/dotfiles/zshrc.sh
