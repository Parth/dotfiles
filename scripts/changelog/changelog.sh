#!/bin/bash

# AUTHOR      : avimehenwal
# DATE        : 13 - Jul - 2020
# PURPOSE     : changelog
# FILENAME    : changelog.sh
#
# Generate changelog from gitlogs

source ../common.sh
LOC='/home/avi/GIT/python.avimehenwal'

# cc = Conventional Commits 9
CC=('feat' 'build' 'docs' 'refac' 'fix' 'ci' 'chore' 'perf' 'test')
# POINT=refs/tags/1.1.1
# POINT=''
SINCE='Jul 13, 2020'

echo -e "# Changelog"
echo -e "\nhttps://en.wikipedia.org/wiki/Changelog \n"
echo -e "[Inspirations](https://www.google.com/search?q=changelog) \n"
echo -e "## From $POINT\n"

for ITEM in "${CC[@]}"
do
    # log $ITEM
    itemformat="### $ITEM"
    printf '%s\n' "$itemformat" | awk '{ print toupper($0) }'
    echo -e
    # Run git command in another directory
    # git --git-dir=$LOC.git shortlog --pretty=oneline $POINT.. --grep=^$ITEM
    git --git-dir=$LOC"/.git" log --format="%Cred%s%Creset%n %Cgreen%b%Creset %n%Cblue%N%Creset" --since="$SINCE" --regexp-ignore-case --grep=^$ITEM
    # git --git-dir=$LOC.git log --pretty=oneline $POINT.. --grep=^$ITEM
    echo -e
done

# Breaking Change Patters
# ^BREAKING
# ^Breaking
# ^breaking
# --grep=!

# git log --oneline --decorate --color --regexp-ignore-case --no-merges --grep=^feat > Changelog


# END
