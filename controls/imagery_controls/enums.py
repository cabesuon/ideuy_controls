"""Module that contains the enumerates for the image controls.

Enumerates:
  Rule.
"""

from enum import Enum

class Control(Enum):
  """Enumerate of controls"""
  pixel_size = 'pixel_size'
  bands_len = 'bands_len'
  dig_level = 'dig_level'
  rad_balance = 'rad_balance'
  srid = 'srid'
  nodata = 'nodata'
  aall = 'aall'
