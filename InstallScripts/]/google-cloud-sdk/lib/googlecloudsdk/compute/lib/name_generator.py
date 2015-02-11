# Copyright 2014 Google Inc. All Rights Reserved.

"""A module for generating resource names."""
import cStringIO
import random
import string

_LENGTH = 12
_BEGIN_ALPHABET = string.ascii_lowercase
_ALPHABET = _BEGIN_ALPHABET + string.digits


def GenerateRandomName():
  """Generates a random string.

  Returns:
    The returned string will be 12 characters long and will begin with
    a lowercase letter followed by 10 characters drawn from the set
    [-a-z0-9] and finally a character drawn from the set [a-z0-9].
  """
  buf = cStringIO.StringIO()
  buf.write(random.choice(_BEGIN_ALPHABET))
  for _ in xrange(_LENGTH - 1):
    buf.write(random.choice(_ALPHABET))
  return buf.getvalue()
