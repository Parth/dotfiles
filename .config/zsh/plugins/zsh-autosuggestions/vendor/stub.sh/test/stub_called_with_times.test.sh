#! /usr/bin/env bash
source "test-helper.sh"

#
# stub_called_with_times() tests.
#

# Echoes 0 when stub doesn't exist.
assert 'stub_called_with_times "cowabunga-dude"' "0"

# Echoes how many times a stub has been called with given arguments
stub "uname"
uname
uname -r
uname -r
uname -r -a
uname -r -a
uname -r -a
assert 'stub_called_with_times "uname"' "1"
assert 'stub_called_with_times "uname" -r' "2"
assert 'stub_called_with_times "uname" -r -a' "3"
assert 'stub_called_with_times "uname" -a' "0"

# Keeps track of identical argument calls to different stubs.
stub "top"
top
top
top -r
top -r
top -r
top -r -a
assert 'stub_called_with_times "top"' "2"
assert 'stub_called_with_times "top" -r' "3"
assert 'stub_called_with_times "top" -r -a' "1"
assert 'stub_called_with_times "top" -a' "0"

# Teardown.
restore "uname"
restore "top"


# End of tests.
assert_end "stub_called_with_times()"
