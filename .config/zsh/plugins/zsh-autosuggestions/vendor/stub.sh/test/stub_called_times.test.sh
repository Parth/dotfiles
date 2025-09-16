#! /usr/bin/env bash
source "test-helper.sh"

#
# stub_called_times() tests.
#

# Echoes 0 if the command isn't stubed.
assert 'stub_called_times "top"' "0"

# Echoes the number of times a stub was called.
stub "uname"
assert 'stub_called_times "uname"' "0"
uname
assert 'stub_called_times "uname"' "1"
uname
assert 'stub_called_times "uname"' "2"
uname
assert 'stub_called_times "uname"' "3"
restore "uname"

# Echoes 0 after a called stub has been recreated.
stub "uname"
uname
assert 'stub_called_times "uname"' "1"
restore "uname"
assert 'stub_called_times "uname"' "1"
stub "uname"
assert 'stub_called_times "uname"' "0"
restore "uname"


# End of tests.
assert_end "stub_called_times()"
