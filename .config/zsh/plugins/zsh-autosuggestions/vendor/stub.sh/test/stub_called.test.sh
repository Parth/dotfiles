#! /usr/bin/env bash
source "test-helper.sh"

#
# stub_called() tests.
#

# Returns 1 when stub doesn't exist.
assert_raises 'stub_called "uname"' 1

# Returns 1 when stub hasn't been called.
stub "uname"
assert_raises 'stub_called "uname"' 1
restore "uname"

# Returns 0 when stub has been called.
stub "uname"
uname
assert_raises 'stub_called "uname"' 0
restore "uname"

# Stub called state is reset by creating a new stub, not by restore.
stub "uname"
uname
restore "uname"
assert_raises 'stub_called "uname"' 0
stub "uname"
assert_raises 'stub_called "uname"' 1
restore "uname"

# Recreating a stub only resets called state of recreated stub.
stub "uname"
stub "top"
uname
top
stub "uname"
assert_raises 'stub_called "uname"' 1
assert_raises 'stub_called "top"' 0
restore "uname"
restore "top"


# End of tests.
assert_end "stub_called()"
