time_out () { perl -e 'alarm shift; exec @ARGV' "$@"; }

echo "Updating rc files"
(cd ~/dotfiles && time_out 2 git pull)
source ~/dotfiles/zshrc.sh
