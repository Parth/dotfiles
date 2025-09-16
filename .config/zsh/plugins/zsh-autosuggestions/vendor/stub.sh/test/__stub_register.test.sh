#! /usr/bin/env bash
source "test-helper.sh"

#
# __stub_register() tests.
#

# Sets up stub index, stub call list, and adds stub to index.
__stub_register "uname"
__stub_register "top"
assert 'echo ${STUB_INDEX[@]}' 'uname=0 top=1'
assert 'echo ${STUB_INDEX[0]}' 'uname=0'
assert 'echo ${STUB_INDEX[1]}' 'top=1'
assert 'echo $STUB_NEXT_INDEX' "2"

# Note: There seems to be no possible way to validate if a empty array
# variable has been set, as it appears to be empty/null/undefined whatever I
# try.


# End of tests.
assert_end "__stub_register()"
