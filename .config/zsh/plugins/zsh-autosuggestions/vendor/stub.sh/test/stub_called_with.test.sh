#! /usr/bin/env bash
source "test-helper.sh"

#
# stub_called_with() tests.
#

# Returns 1 when stub doesn't exist.
assert_raises 'stub_called_with "top"' 1

# Returns 0 when stub has been called with given arguments.
stub "uname"
uname
uname -r
uname -r -a
assert_raises 'stub_called_with "uname"' 0
assert_raises 'stub_called_with "uname" -r' 0
assert_raises 'stub_called_with "uname" -r -a' 0
restore "uname"

# Returns 1 when stub has not been called with given arguments.
stub "uname"
uname -r
assert_raises 'stub_called_with "uname"' 1
assert_raises 'stub_called_with "uname" -a' 1
restore "uname"

# Only matches against exact argument lists.
stub "uname"
uname -r -a
assert_raises 'stub_called_with "uname" -r' 1
assert_raises 'stub_called_with "uname" -r -a' 0
restore "uname"

# Call history is only reset when restubbing a command, not when restoring.
stub "uname"
uname -r
assert_raises 'stub_called_with "uname" -r' 0
restore "uname"
assert_raises 'stub_called_with "uname" -r' 0
stub "uname"
assert_raises 'stub_called_with "uname" -r' 1
restore "uname"

# Handling of string arguments containing spaces.
stub "uname"
uname -r "foo bar"
assert_raises 'stub_called_with "uname" -r "foo bar"' 0
assert_raises 'stub_called_with "uname" -r foo bar' 0
restore "uname"


# End of tests.
assert_end "stub_called_with()"
