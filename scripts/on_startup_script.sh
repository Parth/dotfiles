#!/bin/bash

# AUTHOR      : avimehenwal
# DATE        : 27 - May - 2020
# PURPOSE     : Run operations at system startup
# FILENAME    : on_startup_script.sh
#
# 1. Pull latest configurations from dotfiles, useful when working on multiple machines


source ./common.sh


test_exit_code () {
    EXITCODE=$1
    test $EXITCODE -eq 0 && info "dotfiles up-to-date" || error "Could not update dotfiles $EXITCODE"
    # exit $EXITCODE
}

print_cron_logs () {
    # journalctl -u cron.service
    debug "printing cron logs"
    journalctl -t CROND
}

pull_dotfiles () {
    debug "Pulling dotfiles"
    git --git-dir=$HOME/.dotfiles/ --work-tree=$HOME pull | tee --append $LOG_FILE
    test_exit_code $?
}



# MAIN

pull_dotfiles
# print_cron_logs
# test_logs

# END
