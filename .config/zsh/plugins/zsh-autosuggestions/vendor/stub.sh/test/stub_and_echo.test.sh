#! /usr/bin/env bash
source "test-helper.sh"

#
# stub_and_echo() tests.
#


# Stubbing a bash function.
my-name-is() { echo "My name is $@."; }
assert "my-name-is Edward Elric" "My name is Edward Elric."

stub_and_echo "my-name-is" "Hohenheim"
assert "my-name-is" "Hohenheim"
assert "my-name-is Edward" "Hohenheim"
assert "my-name-is Edward Elric" "Hohenheim"
unset -f my-name-is


# Stubbing a executable file.
stub_and_echo "uname" "State Alchemist"
assert "uname" "State Alchemist"
assert "uname -h" "State Alchemist"
unset -f uname


# Redirect stub output to STDERR.
my-name-is() { echo "My name is $@."; }
stub_and_echo "my-name-is" "Hohenheim" STDERR
assert "my-name-is Edward" ""
assert "my-name-is Edward 2>&1" "Hohenheim"
unset -f my-name-is


# Stubbing something that doesn't exist.
stub_and_echo "cowabunga-dude" "Surf's up dude :D"
assert "cowabunga-dude" "Surf's up dude :D"
assert "cowabunga-dude yeah dude" "Surf's up dude :D"
unset -f cowabunga-dude


# End of tests.
assert_end "stub_and_echo()"
