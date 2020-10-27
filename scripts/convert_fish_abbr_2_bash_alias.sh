#!/bin/bash

# AUTHOR      : avimehenwal
# DATE        : 28 - May - 2020
# PURPOSE     : Reusable aliases in all shells zsh|bash|fish
# FILENAME    : convert_fish_abbr_2_bash_alias.sh
#
# Reuse aliases in all shells (zsh|bash|fish)
#
# - seperate name and values tokens
# - skip lines starting with #
# - skip empty lines
# + Add statistics, # aliases generated, written to file
# +! command substitution syntax fish () replace with bash $()
# +! command chaining syntax

# Use absolute paths instead of relative paths to run scripts from anywhere
# https://stackoverflow.com/questions/192292/how-best-to-include-other-scripts
source "$(dirname $0)/common.sh"

ABBR_FILE="$(dirname $0)/shared_abbreviations.fish"
OUT_FILE="$HOME/.bash_aliases"
BANNER="bash alias"

function empty_file () {
    local NAME=$1
    info "Clear file $NAME contents"
    : > $NAME
    debug "exit code [$?]"
}

function generate_bash_aliases () {
    local IN_FILE=$1
    if [ "$#" == "1" ]; then
        grep --invert-match '^#' $IN_FILE |               # remove lines starting with #
        grep --invert-match --regexp='^$' |               # remove blank lines
        while IFS= read -r line; do
            NAME=$(echo $line | awk '{print $2}')
            VALUE=$(echo $line | awk -F'"' '{print $2}')
            echo -e "alias $NAME='$VALUE'"
        done
        return 0
    else
        echo "Number of arguments=$# do not match"
        return 1
    fi
}

# MAIN
empty_file $OUT_FILE
# generate_bash_aliases $ABBR_FILE | tee --append $OUT_FILE
generate_bash_aliases $ABBR_FILE >> $OUT_FILE
# generate_bash_aliases $ABBR_FILE
info "done"

# END
