#! /usr/bin/env bash
source "test-helper.sh"

#
# stub() tests.
#


# Stubbing a bash function.
my-name-is() { echo "My name is $@."; }
assert "my-name-is Edward Elric" "My name is Edward Elric."
stub "my-name-is"
assert "my-name-is" ""
unset -f my-name-is


# Stubbing a executable file.
stub "uname"
assert "uname" ""
unset -f uname


# Redirect stub of bash function output to STDOUT.
my-name-is() { echo "My name is $@."; }
stub "my-name-is" STDOUT
assert "my-name-is" "my-name-is stub: "
assert "my-name-is Edward" "my-name-is stub: Edward"
assert "my-name-is Edward Elric" "my-name-is stub: Edward Elric"
unset -f my-name-is


# Redirect stub of executable file output to STDOUT.
stub "uname" STDOUT
assert "uname" "uname stub: "
assert "uname -r" "uname stub: -r"
unset -f my-name-is


# Redirect stub of bash function output to STDERR.
my-name-is() { echo "My name is $@."; }
stub "my-name-is" STDERR
assert "my-name-is Edward" ""
assert "my-name-is Edward 2>&1" "my-name-is stub: Edward"
unset -f my-name-is


# Redirect stub of executable output to STDERR.
stub "uname" STDERR
assert "uname -r" ""
assert "uname 2>&1" "uname stub: "
assert "uname -r 2>&1" "uname stub: -r"
unset -f my-name-is


# Redirect stub of bash function output to /dev/null.
my-name-is() { echo "My name is $@."; }
stub "my-name-is" null
assert "my-name-is Edward" ""
assert "my-name-is Edward 2>&1" ""
unset -f my-name-is


# Stubbing something that doesn't exist.
assert_raises "cowabunga-dude" 127
stub "cowabunga-dude" stdout
assert_raises "cowabunga-dude" 0
assert "cowabunga-dude yeah dude" "cowabunga-dude stub: yeah dude"
unset -f cowabunga-dude


# End of tests.
assert_end "stub()"
