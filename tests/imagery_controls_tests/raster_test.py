"""Module that contains the unit tests for controls.imagery_controls.raster.

Examples:
  $python -m unittest raster_test.py

Classes:
  TestRasterManager.
"""
import unittest
import gettext
import os
from controls.imagery_controls.raster import (
  RasterManager
)

class TestRasterManager(unittest.TestCase):
  """Class to manage unit test of RasterManager methods.

  Attributes:
      rman: RasterManager instance.
  """
  def setUp(self):
    self._ = gettext.gettext
    self.cdir = os.path.dirname(os.path.realpath(__file__))
    self.rman = RasterManager(os.path.join(self.cdir, 'img1.tif'))

  def test_get_raster_units_per_pixel(self):
    """Unit test of RasterManager method get_raster_units_per_pixel."""
    self.assertTrue(
      (
        [2.5, -2.5] ==
        self.rman.get_raster_units_per_pixel()
      ),
      self._('incorrect raster units per pixel')
    )

  def test_get_raster_bands_len(self):
    """Unit test of RasterManager method get_bands_len."""
    print()
    self.assertTrue(
      self.rman.get_raster_bands_len() == 1,
      self._('incorrect raster bands len')
    )

  def test_get_raster_bands_datatype(self):
    """Unit test of RasterManager method get_raster_bands_datatype."""
    self.assertTrue(
      (
        [6] ==
        self.rman.get_raster_bands_datatype()
      ),
      self._('incorrect raster bands datatype')
    )

  def test_get_raster_bands_rad_balance(self):
    """Unit test of RasterManager method get_raster_bands_rad_balance."""
    self.assertTrue(
      (
        [[
            302.46136474609,
            334.39392089844,
            305.4859783935509,
            331.0499816894556,
            526,
            2941,
            1.4893,
            8.327
        ]] ==
        self.rman.get_raster_bands_rad_balance(0.01)
      ),
      self._('incorrect raster bands radiometric balance')
    )

  def test_get_raster_bands_nodata(self):
    """Unit test of RasterManager method get_raster_bands_nodata."""
    self.assertTrue(
      (
        [0] ==
        self.rman.get_raster_bands_nodata()
      ),
      self._('incorrect raster bands nodata')
    )
