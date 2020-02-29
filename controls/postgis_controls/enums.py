"""Module that contains the enumerates for the postgis controls.

Enumerates:
  Rule.
"""

from enum import Enum

class Rule(Enum):
  """Enumerate of control rules"""
  invalid = 'invalid'
  duplicate = 'duplicate'
  multipart = 'multipart'
  intersect = 'intersect'
  null = 'null'
  aall = 'all'
