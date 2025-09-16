#! /usr/bin/env bash
source "test-helper.sh"

#
# stub_called_at_most_times() tests.
#

# Setup
stub "uname"
uname
uname
uname

# Returns 0 when stub called no more than given number of times.
assert_raises 'stub_called_at_most_times "uname" 5' 0
assert_raises 'stub_called_at_most_times "uname" 4' 0
assert_raises 'stub_called_at_most_times "uname" 3' 0

# Returns 1 when stub has been called more than given number of times.
assert_raises 'stub_called_at_most_times "uname" 2' 1
assert_raises 'stub_called_at_most_times "uname" 1' 1
assert_raises 'stub_called_at_most_times "uname" 0' 1

# Behaves as if stub has not been called when the stub doesn't exist.
assert_raises 'stub_called_at_most_times "top" 0' 0
assert_raises 'stub_called_at_most_times "top" 1' 0

# Teardown
restore "uname"


# End of tests.
assert_end "stub_called_at_most_times()"
