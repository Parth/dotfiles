#!/usr/bin/fish
#
# AUTHOR      : avimehenwal
# DATE        : 29 - May - 2020
# PURPOSE     : Shared Fish Abbreviations
#
# Use double quotes instead of single quotes

# Short commands
abbr d          "git --git-dir=$HOME/.dotfiles/ --work-tree=$HOME"
abbr m          "man"
abbr r          "ranger"
# copy paste to system clipboard doesnt work on VIM due to -xterm_clipboard
abbr v          "nvim"
abbr pwd        "pwd | tee /dev/tty | xclip -selection clip"

# git related
abbr gcl        "git clone"
abbr gcm        "git checkout master"
abbr gcd        "git checkout develop"
# abbr gco        "git checkout (git.branch.name)"
# abbr stage      "git add (git.stage.list)"
abbr ggpull     "git pull --all"
abbr ggpush     "git pull --all; git push; git push --tags"
abbr refresh    "source $HOME/.config/fish/config.fish"
abbr watch      "watch --color --differences --beep --interval 2"
abbr path       "readlink -f"
abbr file       "file --mime"
abbr psl        "process.list"
abbr alert      "notify-send --urgency=normal 'DONE'"
abbr logout     "gnome-session-quit"
abbr anki       "~/mySoftwares/anki-2.1.14-linux-amd64/bin/anki"
abbr listhosts  "sed -rn "s/^\s*Host\s+(.*)\s*/\1/ip" ~/.ssh/config"
abbr c          "xclip -selection clip"
abbr du         "du --human-readable --count-links"
abbr cat        "bat"
abbr pls        "fuck"
abbr dd         "dd status=progress conv=sparse count=1 bs=4096"
abbr gst        "tig status"
abbr open       "xdg-open"
abbr release    "git checkout master; git branch; git merge develop; git pull --all; and git push; and git push --tags ; git checkout develop; git branch"
abbr rc         "source ~/.config/fish/config.fish"
abbr pping      "prettyping"
abbr fishrc     "code /home/avi/.config/fish/config.fish"
# abbr dotfile    "code '(cd ;git --git-dir=$HOME/.dotfiles/ --work-tree=$HOME ls | fzf --multi)'"
abbr note       "cd $HOME/REPO/avimehenwal2; git pull; code -n ."

# colourize cat output
abbr ccat       "pygmentize -g"
abbr dmesg      "dmesg --human --color=always"
# fuzzy finding with previews
# abbr fzf "fzf --preview "bat --color "always" {}""
abbr diff       "diff --unified=3 --color=always"
abbr ipinfo     "curl  -H "Accept: application/json" ipinfo.io/json"
abbr termgraph  "termgraph --custom-tick "▇""

# GIT FLOW
abbr gfi        "git flow init; and git push --set-upstream origin develop; and git push"
abbr gffs       "git flow feature start"
abbr gfrs       "git flow release start"
abbr gffp       "git flow feature publish"
abbr gfrp       "git flow release publish"
abbr gfff       "git flow feature finish"
abbr gfrf       "git flow release finish"

# Quick Navigation
abbr ..         "cd .."
abbr ...        "cd ../.."
abbr ....       "cd ../../../"
abbr etc        "cd /etc"
abbr sbin       "cd /usr/sbin/"
abbr json       "python3 -m json.tool | pygmentize -l json"
abbr tar        "tar --verbose --gzip --extract --file"
abbr ip         "ip --color=always"
abbr ipa        "ip --color=always -brief addr show"
abbr ipls       "ip --color=always -details -stats -iec -human link show wlan0"
abbr ll         " ls --classify --color=always --group-directories-first --block-size=K -halt $argv | less"
abbr h          "bat --language yaml --theme "Sublime Snazzy""

# Monitoring
abbr syslog     "sudo tail --lines 20 --follow /var/log/syslog | ccze"

# MIRROR DIMENSION
abbr sandbox    "docker run --interactive --tty --rm apline sh"
abbr ubuntu     "docker run --interactive --tty ubuntu bash"
abbr py3        "docker run -it --rm frolvlad/alpine-python3 python3"
abbr up         "lxc list; and lxc start ubuntu18; lxc exec ubuntu18 -- /usr/bin/fish"
abbr down       "lxc stop ubuntu18; and lxc list"
abbr test       "pwd; and ls"
abbr dm         "docker-machine"
abbr mon        "portainer_docker"

# VAGRANT
abbr vgs        "vagrant global-status --prune"
abbr vs         "vagrant status"
abbr vu         "vagrant validate; and vagrant up --parallel; and vagrant ssh"
abbr vr         "vagrant reload"
abbr vh         "vagrant halt; and vagrant status"
abbr vr         "vagrant reload; and vagrant status; and vagrant ssh"

# Linux Commands
abbr pstree     "ps -ejH"
abbr venv       "python3 -m venv venv; and source venv/bin/activate.fish"
abbr chmod      "chmod --verbose"

abbr lscron     "crontab -l | bat --language yaml"

# Fundamental linux commands enhancements
abbr mv         "mv --interactive --verbose"

# END