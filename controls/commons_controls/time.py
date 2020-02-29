"""Util module that contains the tools to meassure execution time of a control.

Enumerates:
  TimeUnit.

Functions:
  get_time.
  get_duration.

Classes:
  TimeManagerError.
  TimeManager.
"""
import gettext
import logging
from enum import Enum
from datetime import datetime, timedelta

class TimeUnit(Enum):
  """Enumerate of time units."""
  second = 0
  minute = 1
  hour = 2
  day = 3

def get_time():
  """Function to obtain current time.

  Returns:
    datetime object.
  """
  return datetime.now()

def get_str_time():
  """Function to obtain current time.

  Returns:
    datetime object.
  """
  return datetime.now().strftime('%m-%d-%Y')

def get_duration(start, end, unit=TimeUnit.second):
  """Function to obtain the time duration, in unit, between two datetimes.

  Args:
    start: Initial datetime.
    end: End datetime.
    unit: Unit of the return duration.

  Returns:
    Duration in time unit.
  """
  if not start or not end:
    return None
  duration = int(timedelta.total_seconds(end - start))
  if unit.value > TimeUnit.second.value:
    duration = duration / 60
  if unit.value > TimeUnit.minute.value:
    duration = duration / 60
  if unit.value > TimeUnit.hour.value:
    duration = duration / 24
  return duration

class TimeManagerError(Exception):
  """Exception for TimeManager."""

class TimeManager:
  """Class to manage time execution of a control.

  Attributes:
      logger: Logging object.
      dt_start: Initial datetime.
      dt_end: End datetime.
  """

  def __init__(self, logger=None):
    # parameters
    self.logger = logger or logging.getLogger(__name__)
    self.dt_start = None
    self.dt_end = None
    # internal
    self._ = gettext.gettext

  def start(self):
    """Method to set the initial datetime."""
    self.dt_start = get_time()

  def end(self):
    """Method to set the end datetime."""
    self.dt_end = get_time()

  def time(self, unit=TimeUnit.second):
    """Method to obtain the time duration, in unit, of the execution.

    Args:
      unit: Unit of the return duration.

    Returns:
      Duration in time unit.

    Raises:
      TimeManagerError
    """
    if not self.dt_start:
      raise TimeManagerError(self._('Time not started'))
    if not self.dt_end:
      raise TimeManagerError(self._('Time not ended'))
    return get_duration(self.dt_start, self.dt_end, unit)
