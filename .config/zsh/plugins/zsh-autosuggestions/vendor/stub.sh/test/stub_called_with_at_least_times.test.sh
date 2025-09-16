#! /usr/bin/env bash
source "test-helper.sh"

#
# stub_called_with_at_least_times() tests.
#

# Setup.
stub "uname"
uname
uname -r
uname -r
uname -r -a

# Retruns 0 when stub called with at least given number of times.
assert_raises 'stub_called_with_at_least_times "uname" 0 -r' 0
assert_raises 'stub_called_with_at_least_times "uname" 1 -r' 0
assert_raises 'stub_called_with_at_least_times "uname" 2 -r' 0

# Retruns 1 when stub called with less than given number of times.
assert_raises 'stub_called_with_at_least_times "uname" 3 -r' 1
assert_raises 'stub_called_with_at_least_times "uname" 4 -r' 1
assert_raises 'stub_called_with_at_least_times "uname" 5 -r' 1

# Behaves as if stub has not been called when the stub doesn't exist.
assert_raises 'stub_called_with_at_least_times "top" 0' 0
assert_raises 'stub_called_with_at_least_times "top" 1' 1

# Teardown.
restore "uname"


# End of tests.
assert_end "stub_called_with_at_least_times()"
