#! /usr/bin/env bash
source "test-helper.sh"

#
# __stub_index() tests.
#

# Echoes index of given stub.
STUB_INDEX=("uname=1" "top=3")
assert '__stub_index "uname"' "1"
assert '__stub_index "top"' "3"
unset STUB_INDEX

# Echoes nothing if stub is not in the index.
STUB_INDEX=("uname=1")
assert '__stub_index "top"' ""
unset STUB_INDEX


# End of tests.
assert_end "__stub_index()"
