[ -n "$TEST_DEBUG" ] && set -x

# Set testroot variable.
testroot="$(dirname "$BASH_SOURCE")"

# Include assert.sh testing library.
source "$testroot/assert.sh"
source "$testroot/../stub.sh"

