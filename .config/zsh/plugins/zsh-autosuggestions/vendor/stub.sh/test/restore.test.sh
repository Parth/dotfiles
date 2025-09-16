#! /usr/bin/env bash
source "test-helper.sh"

#
# restore() tests.
#


# Stubbing and restoring a bash function.
my-name-is() { echo "My name is $@."; }
assert "my-name-is Edward Elric" "My name is Edward Elric."

stub "my-name-is" stdout
assert "my-name-is Edward Elric" "my-name-is stub: Edward Elric"

restore "my-name-is" stdout
assert "my-name-is Edward Elric" "My name is Edward Elric."


# Stubbing and restoring a executable file.
actual_uname="$(uname)"
stub "uname" stdout
assert "uname" "uname stub: "
assert "uname -a" "uname stub: -a"

restore "uname"
assert "uname" "$actual_uname"


# Stubbing and restoring something that doesn't exist.
assert_raises "cowabunga-dude" 127
stub "cowabunga-dude"
assert_raises "cowabunga-dude" 0
restore "cowabunga-dude"
assert_raises "cowabunga-dude" 127


# Attempting to restore a function that wasn't stubbed.
my-name-is() { echo "My name is $@."; }
assert "my-name-is Edward Elric" "My name is Edward Elric."

restore "my-name-is"
assert "my-name-is Edward Elric" "My name is Edward Elric."


# Stubbing the same function multiple times and then restoring it.
my-name-is() { echo "My name is $@."; }
stub "my-name-is"
assert "my-name-is Edward Elric" ""
stub "my-name-is" stdout
assert "my-name-is Edward Elric" "my-name-is stub: Edward Elric"

restore "my-name-is"
assert "my-name-is Edward Elric" "My name is Edward Elric."



# End of tests.
assert_end "restore()"
