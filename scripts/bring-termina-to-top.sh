#!/bin/bash

# AUTHOR      : avimehenwal
# DATE        : 17-Oct-2020
# PURPOSE     : Bring Terminal on top Hotkey
# FILENAME    : bring-termina-to-top.sh
#
# Bring terminal on top Hotkey <F9>
# With ubuntu, use <SUPER + 2>

DEPENDENCY=(xdotool)

substring_match() {
    SUB=$1
    STR=$2
    if [[ "$STR" == *"$SUB"* ]]; then
        return 0
    else
        return 1
    fi
}

provide_package() {
  PKG=$1
  echo "testing $PKG"
  STRING=$(dpkg --status $PKG | grep Status)
  substring_match "ok installed" $STRING || sudo apt install -y $PKG
}

# for item in ${DEPENDENCY[@]}
# do
#     provide_package $item
# done

# MAIN

# Favourite 1
xdotool mousemove 35 63 click 1 mousemove restore
# Favourite 2
# xdotool mousemove 31 131 click 1 mousemove restore

# END
