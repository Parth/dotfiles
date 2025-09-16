#! /usr/bin/env bash
source "test-helper.sh"

#
# stub_and_eval() tests.
#


# Stubbing a bash function.
my-name-is() { echo "My name is $@."; }
assert "my-name-is Edward Elric" "My name is Edward Elric."

stub_and_eval "my-name-is" "date +%Y"
assert "my-name-is" "$(date +%Y)"
assert "my-name-is Edward" "$(date +%Y)"
assert "my-name-is Edward Elric" "$(date +%Y)"
unset -f my-name-is


# Stubbing a executable file.
stub_and_eval "uname" "date +%Y"
assert "uname" "$(date +%Y)"
assert "uname -h" "$(date +%Y)"
unset -f uname


# Stubbing something that doesn't exist.
stub_and_eval "cowabunga-dude" "date +%Y"
assert "cowabunga-dude" "$(date +%Y)"
assert "cowabunga-dude yeah dude" "$(date +%Y)"
unset -f cowabunga-dude


# End of tests.
assert_end "stub_and_eval()"
