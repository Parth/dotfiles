autoload bashcompinit
bashcompinit

_python_argcomplete() {
    local IFS=''
    COMPREPLY=( $(IFS="$IFS"                   COMP_LINE="$COMP_LINE"                   COMP_POINT="$COMP_POINT"                   _ARGCOMPLETE_COMP_WORDBREAKS="$COMP_WORDBREAKS"                   _ARGCOMPLETE=1                   "$1" 8>&1 9>&2 1>/dev/null 2>/dev/null) )
    if [[ $? != 0 ]]; then
        unset COMPREPLY
    fi
}
complete -o nospace -o default -F _python_argcomplete "gcloud"

_completer() {
    command=$1
    name=$2
    eval '[[ -n "$'"${name}"'_COMMANDS" ]] || '"${name}"'_COMMANDS="$('"${command}"')"'
    set -- $COMP_LINE
    shift
    while [[ $1 == -* ]]; do
          shift
    done
    [[ -n "$2" ]] && return
    grep -q "${name}\s*$" <<< $COMP_LINE &&
        eval 'COMPREPLY=($'"${name}"'_COMMANDS)' &&
        return
    [[ "$COMP_LINE" == *" " ]] && return
    [[ -n "$1" ]] &&
        eval 'COMPREPLY=($(echo "$'"${name}"'_COMMANDS" | grep ^'"$1"'))'
}

unset bq_COMMANDS
_bq_completer() {
    _completer "CLOUDSDK_COMPONENT_MANAGER_DISABLE_UPDATE_CHECK=1 bq help | grep '^[^ ][^ ]*  ' | sed 's/ .*//'" bq
}

unset gcutil_COMMANDS
_gcutil_completer() {
    _completer "CLOUDSDK_COMPONENT_MANAGER_DISABLE_UPDATE_CHECK=1 gcutil help | grep -v '^information' | grep '^[a-z]' | sed -e 's/ .*//' -e '/^$/d'" gcutil
}

complete -o default -F _bq_completer bq
complete -o nospace -F _python_argcomplete gsutil
complete -o default -F _gcutil_completer gcutil

