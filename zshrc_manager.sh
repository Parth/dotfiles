echo "Updating rc files"
(cd ~/dotfiles && timeout 3 git pull)
source ~/dotfiles/zshrc.sh
