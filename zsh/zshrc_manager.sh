time_out () { perl -e 'alarm shift; exec @ARGV' "$@"; }

# Run tmux if exists
if command -v tmux>/dev/null; then
	[ -z $TMUX ] && exec tmux
else 
	echo "tmux not installed. Run ./deploy to configure dependencies"
fi

echo "Checking for updates."
#(cd ~/dotfiles && time_out 3 git pull && time_out 3 git submodule update --init --recursive)
(cd ~/dotfiles && git fetch)

if (( $(cd ~/dotfiles && git rev-list HEAD...origin/master | wc -l) > 0 )) 
then
	echo "Updates Detected:"
	cd ~/dotfiles && git log ..@{u} --pretty=format:%Cred%aN:%Creset\ %s\ %Cgreen%cd
	echo "Setting up..."
	cd ~/dotfiles && git pull -q && git submodule update --init --recursive
else
	echo "Already up to date."
fi

source ~/dotfiles/zsh/zshrc.sh
