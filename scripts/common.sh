#!/bin/bash

# AUTHOR      : avimehenwal
# DATE        : 27 - May - 2020
# PURPOSE     : Shared Functions
# FILENAME    : common.sh
#
# 1. Logging functionsw
# 2. coloured logs
# 3. Write logs to a file with timestamp
#
# []. Install if command not found


LOG_FILE="$HOME/aviscripts/on_startup_script.log"
BANNER="avi scripts"

# https://misc.flogisoft.com/bash/tip_colors_and_formatting
NORMAL="\e[0m"
BOLD="\e[1m"
BOLD_RESET="\e[21m"          # doesnt seems to work
UNDERLINE="\e[4m"
BLINK="\e[5m"

RED="\e[31m"
GREEN="\e[32m"
YELLOW="\e[33m"
BLUE="\e[34m"
CYAN="\e[36m"


log () {
    COLOR=$1
    PREFIX=$2
    MSG=$3
    TIMESTAMP="$CYAN$(date)$NORMAL"
    echo -e "$TIMESTAMP$COLOR $BOLD$PREFIX$NORMAL $COLOR$MSG $NORMAL" | tee --append $LOG_FILE
    # printf "fun=%s,book=%s\n" "${fun}" "${book}"
}

debug () {
    prefix="DEBUG ::"
    log "$BLUE" "$prefix" "$1"
}

info () {
    prefix="INFO  ::"
    log "$GREEN" "$prefix" "$1"
}

warning () {
    prefix="WARN  ::"
    log "$YELLOW" "$prefix" "$1"
}

error () {
    prefix="ERROR ::"
    log "$RED" "$prefix" "$1"
}

test_logs () {
    debug "Some debug message"
    info "Some info message"
    warning "Some warning message"
    error "Some error message"
}

print_banner () {
    clear
    toilet --filter border --font standard --gay --termwidth $BANNER
}

if command -v toilet >/dev/null 2>&1 ; then
  print_banner
else
  sudo apt install -y toilet
  print_banner
fi

# Move it to other file. Seperation of concern
# Substring match
substring_match() {
    SUB=$1
    STR=$2
    if [[ "$STR" == *"$SUB"* ]]; then
        return 0
    else
        return 1
    fi
}
# substring_match "Linux" 'GNU/Linux is an operating system'
# substring_match "siofidsofi" 'GNU/Linux is an operating system'

# Check if package already installed else install it
provide_package() {
    PKG=$1
    echo "testing $PKG"
    STRING=$(dpkg --status $PKG | grep Status)
    substring_match "ok installed" $STRING || sudo apt install -y $PKG
}

# provide_package fonts-powerline


# END
