#! /usr/bin/env bash
source "test-helper.sh"

#
# __stub_call() tests.
#

# Adds call to stub call list.
STUB_INDEX=("uname=0")
STUB_0_CALLS=()
__stub_call "uname"
__stub_call "uname" -r
__stub_call "uname" -r -a
assert 'echo ${STUB_0_CALLS[@]}' "<none> -r -r -a"
assert 'echo ${STUB_0_CALLS[0]}' "<none>"
assert 'echo ${STUB_0_CALLS[1]}' "-r"
assert 'echo ${STUB_0_CALLS[2]}' "-r -a"


# End of tests.
assert_end "__stub_call()"
