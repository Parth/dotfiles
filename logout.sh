confirm Revert dotfiles? Current dotfiles will be deleted. If there is nothing to revert to, you will not have any dotfiles.
rm -rf ~/.zshrc
rm -rf ~/.vimrc

mv ~/temp_dot_files/* ~
rm -rf temp_dot_files

function confirm() {
    echo -n "$@ "
    read -e answer
    for response in y Y yes YES Yes Sure sure SURE OK ok Ok
    do
        if [ "_$answer" == "_$response" ]
        then
            return 0
        fi
    done

    # Any answer other than the list above is considerred a "no" answer
    return 1
}
