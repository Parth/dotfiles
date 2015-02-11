# Copyright 2014 Google Inc. All Rights Reserved.
"""A utility for generating Windows Server passwords.

The requirements for the passwords are outlined in
http://technet.microsoft.com/en-us/library/cc786468(v=ws.10).aspx.
"""

import random
import string

_LENGTH = 12
_CHARACTER_CLASSES = [
    string.ascii_uppercase,
    string.ascii_lowercase,
    string.digits,
    r"""~!@#$%^&*_-+=`|\(){}[]:;"'<>,.?/""",
]
_CLASSES_REQUIRED = 3


def Generate(rand=None):
  """Returns a random password compatible with a Windows Server.

  Args:
    rand: A random-like object. This is useful for testing. If not
      specified, random.SystemRandom() is used which uses the OS CSPRNG.

  Returns:
    A password as a string.
  """
  rand = rand or random.SystemRandom()

  # Generate a password where each character is chosen uniformly at random from
  # the list of all characters. Repeat until the password meets the complexity
  # requirements. Each iteration has a 99.3% chance to succeed.
  all_chars = ''.join(_CHARACTER_CLASSES)
  classes_represented = 0
  while classes_represented < _CLASSES_REQUIRED:
    candidate = [rand.choice(all_chars) for _ in xrange(_LENGTH)]
    candidate_chars = set(candidate)
    classes_represented = sum(not candidate_chars.isdisjoint(chars)
                              for chars in _CHARACTER_CLASSES)
  return ''.join(candidate)

if __name__ == '__main__':
  print Generate()
