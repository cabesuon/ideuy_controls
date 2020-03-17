"""Module that contains the unit tests for controls.imagery_controls.results.

Examples:
  $python -m unittest results_test.py

Classes:
  TestWorldFileData.
  TestPixelSizeResult.
  TestBandsLenResult.
  TestDigitalLevelResult.
  TestRadBalanceResult.
  TestNoDataResult.
"""
import unittest
import gettext
from controls.imagery_controls.results import (
  WorldFileData, PixelSizeResult, BandsLenResult, DigitalLevelResult,
  RadBalanceResult, NoDataResult
)

class TestWorldFileData(unittest.TestCase):
  """Class to manage unit test of WoldFileData methods."""
  def setUp(self):
    self._ = gettext.gettext

  def test_get_units_per_pixel(self):
    """Unit test of WorldFileData method get_units_per_pixel."""
    self.assertTrue(
      (
        [2.5, -2.5] ==
        WorldFileData(
          [2.5, -2.5],
          [0, 0],
          [671303.27899, 6224247.39744]
        ).get_units_per_pixel()
      ),
      self._('incorrect units per pixel')
    )
    self.assertTrue(
      (
        [0.3150908387703457, 0.3150908387703457] ==
        WorldFileData(
          [-0.009114, 0.009114],
          [-0.314959, -0.314959],
          [581314.822358, 6224247.39744]
        ).get_units_per_pixel()
      ),
      self._('incorrect units per pixel')
    )

class TestPixelSizeResult(unittest.TestCase):
  """Class to manage unit test of PixelSizeResult methods."""
  def setUp(self):
    self._ = gettext.gettext

  def test_result_row(self):
    """Unit test of PixelSizeResult method result_row."""
    self.assertTrue(
      (
        [True, 0.099, 0.099, 0.101] ==
        PixelSizeResult([0.099, 0.099], 0.1, 0.01).result_row()
      ),
      self._('incorrect pixel size result')
    )
    self.assertTrue(
      (
        [True, 0.099, 0.099, 0.101] ==
        PixelSizeResult([0.1, -0.099], 0.1, 0.01).result_row()
      ),
      self._('incorrect pixel size result')
    )

class TestBandsLenResult(unittest.TestCase):
  """Class to manage unit test of BandsLenResult methods."""
  def setUp(self):
    self._ = gettext.gettext

  def test_result_row(self):
    """Unit test of BandsLenResult method result_row."""
    self.assertTrue(
      (
        [True, 4] ==
        BandsLenResult(4, 4).result_row()
      ),
      self._('incorrect bands len result')
    )
    self.assertTrue(
      (
        [False, 1] ==
        BandsLenResult(1, 4).result_row()
      ),
      self._('incorrect bands len result')
    )

class TestDigitalLevelResult(unittest.TestCase):
  """Class to manage unit test of DigitalLevelResult methods."""
  def setUp(self):
    self._ = gettext.gettext

  def test_result_row(self):
    """Unit test of DigitalLevelResult method result_row."""
    self.assertTrue(
      (
        [True, '32,32,32,32'] ==
        DigitalLevelResult([4, 4, 4, 4], 32).result_row()
      ),
      self._('incorrect digital level result')
    )
    self.assertTrue(
      (
        [False, '8'] ==
        DigitalLevelResult([1], 16).result_row()
      ),
      self._('incorrect digital level result')
    )

class TestRadBalanceResult(unittest.TestCase):
  """Class to manage unit test of RadBalanceResult methods."""
  def setUp(self):
    self._ = gettext.gettext

  def test_result_row(self):
    """Unit test of RadBalanceResult method result_row."""
    self.assertTrue(
      (
        [
          True,
          '0,256,0,256,10,10,1,1;0,256,0,256,8,17,0.8,1.7;0,256,0,256,2,19,0.2,1.9'
        ] ==
        RadBalanceResult(
          [
            [0, 256, 0, 256, 10, 10, 1, 1],
            [0, 256, 0, 256, 8, 17, 0.8, 1.7],
            [0, 256, 0, 256, 2, 19, 0.2, 1.9]
          ],
          0.02
        ).result_row()
      ),
      self._('incorrect radiometric balance result')
    )
    self.assertTrue(
      (
        [
          False,
          '0,256,0,256,10,10,1,1;0,256,0,256,21,17,2.1,1.7'
        ] ==
        RadBalanceResult(
          [
            [0, 256, 0, 256, 10, 10, 1, 1],
            [0, 256, 0, 256, 21, 17, 2.1, 1.7]
          ],
          0.02
        ).result_row()
      ),
      self._('incorrect radiometric balance result')
    )

class TestNoDataResult(unittest.TestCase):
  """Class to manage unit test of NoDataResult methods."""
  def setUp(self):
    self._ = gettext.gettext

  def test_result_row(self):
    """Unit test of NoDataResult method result_row."""
    self.assertTrue(
      (
        [True, '0.9;0.9;0.2'] ==
        NoDataResult([0.9, 0.9, 0.2], 0.01).result_row()
      ),
      self._('incorrect nodata result')
    )
    self.assertTrue(
      (
        [False, '0;1.2;0'] ==
        NoDataResult([0, 1.2, 0], 0.01).result_row()
      ),
      self._('incorrect nodata result')
    )
