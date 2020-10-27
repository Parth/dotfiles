#!/bin/bash

# AUTHOR      : avimehenwal
# DATE        : 20-Oct-2020
# PURPOSE     : cd until GIT-ROOT
# FILENAME    : cdr.sh
#
# returns directory location where .git/ directory is present

# echo -e "`pwd` \t starting"
while [ ! -d ./.git ]
do
  cd ..
  # echo $(pwd)
done

echo $(pwd)

# END
