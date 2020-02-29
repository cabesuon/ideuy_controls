"""Module that contains the unit tests for controls.commons_controls.time.

Examples:
  $python -m unittest time_test.py

Attributes:
  _: gettext

Classes:
  TestTimeManager.
  TestTimeFunctions.
"""
import unittest
import gettext
import time
from datetime import datetime


from controls.commons_controls.time import (
  TimeManager, TimeManagerError, TimeUnit, get_time, get_duration
)

class TestTimeManager(unittest.TestCase):
  """Class to manage unit test of TimeManager methods.

  Attributes:
      tman: TimeManager instance.
  """
  def setUp(self):
    self._ = gettext.gettext
    self.tman = TimeManager()

  def test_start(self):
    """Unit test of TimeManager method start."""
    dts = datetime.now()
    self.tman.start()
    dte = datetime.now()
    self.assertTrue(
      self.tman.dt_start >= dts and self.tman.dt_start <= dte,
      self._('incorrect start time')
    )

  def test_end(self):
    """Unit test of TimeManager method end."""
    dts = datetime.now()
    self.tman.end()
    dte = datetime.now()
    self.assertTrue(
      self.tman.dt_end >= dts and self.tman.dt_end <= dte,
      self._('incorrect end time')
    )

  def test_time(self):
    """Unit test of TimeManager method time."""
    with self.assertRaises(TimeManagerError):
      self.tman.time(TimeUnit.second)
    self.tman.start()
    with self.assertRaises(TimeManagerError):
      self.tman.time(TimeUnit.second)
    time.sleep(1)
    self.tman.end()
    self.assertTrue(self.tman.time(TimeUnit.second) > 0)

class TestTimeFunctions(unittest.TestCase):
  """Class to manage unit test of time module functions."""

  def setUp(self):
    self._ = gettext.gettext

  def test_get_time(self):
    """Unit test of function get_time."""
    dts = datetime.now()
    val = get_time()
    dte = datetime.now()
    self.assertTrue(
      dts <= val <= dte,
      self._('incorrect get_time return value')
    )

  def test_get_duration(self):
    """Unit test of function get_duration."""
    dts = datetime.now()
    time.sleep(1)
    dte = datetime.now()
    val = get_duration(dts, dte, TimeUnit.second)
    # acepted error 20 miliseconds
    self.assertTrue(
      0.998 <= val <= 1.002,
      self._('incorrect get_duration return value')
    )
