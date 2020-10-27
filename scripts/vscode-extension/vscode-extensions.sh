#!/bin/bash

# AUTHOR      : avimehenwal
# DATE        : 17 - May - 2020
# PURPOSE     : Extension manager for vscode
# FILENAME    : vscode-extensions.sh
#
# Keep track of extensions, version control them, sync them, quickly install them

source ../common.sh

banner="vsCode utils"
REQUIRNMENTS=$HOME/aviscripts/vscode-extension/vscode-extensions.txt

print_help () {
cat << EOF

  AVISCRIPT VSCODE-EXTENSIONS UTILITY

  Kindly select a numer from [1-3]

    [1]. Freeze and write all current extensions to $REQUIRNMENTS
    [2]. Install all extensions from $REQUIRNMENTS
    [3]. Backup and remove all extensions
    [q]. Exit application

EOF
  # read --prompt and other switches with -- do NOT work
  read -p "Enter your choice from above:[1|2|3|q] " -n 1 -i "2" NUM
  echo -e "\n"
  info "you selected $NUM"
}

freeze_extensions () {
  info "Freezing and writing all current extensions to $REQUIRNMENTS"
  debug "code --list-extension"
  code --list-extensions | tee $REQUIRNMENTS
}

install_extensions () {
  info "Installing all extensions from $REQUIRNMENTS"
  debug "code --install-extension <extensionName>"
  awk '{ print "code --install-extension "$1"" | "/bin/bash"}' $REQUIRNMENTS
}

remove_all_extensions () {
  # 3.1 First backuip all extensions by calling 1.
  # 3.2 remove all extensions
  freeze_extensions
  info "code --uninstall-extension <extensionName>"
  awk '{ print "code --uninstall-extension "$1"" | "/bin/bash"}' $REQUIRNMENTS
}

print_banner () {
  clear
  # available fonts at -> ls /usr/share/figlet
  # bigmono9 mono12
  toilet --filter border --font smmono12 --gay --termwidth $banner
}

if command -v toilet >/dev/null 2>&1 ; then
  print_banner
else
  sudo apt install toilet
  print_banner
fi

print_help

case $NUM in
[1])
  freeze_extensions
  ;;
[2])
  echo "::2:: install extension"
  install_extensions
  ;;
[3])
  remove_all_extensions
  ;;
[q])
  exit 0
  ;;
*)
  error "INVALID SELECTION - kindly select a valid number from [1-3]"
  print_help
  ;;
esac


# https://github.com/microsoft/vscode/issues/6099
# END
