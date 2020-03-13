"""Module that contains the results of the imagery controls.

Functions:

Classes:
  WorldFileData.
  PixelSizeResult.
  BandLenResult.
  DigitalLevelResult.
  RadiometricBalanceResult.
  SRIDResult.
  NoDataResult.
"""
import math

class WorldFileData:
  """Class to handle data of a world file.

  Attributes:
    pixel_size: pixel size in the x and y direction in map units/pixel (A, E).
    rotation: rotation about x and y axis (B, D).
    coordinate: x and y coordinate of the center of the upper left pixel (C, F).
  """
  def __init__(self, pixel_size=None, rotation=None, coordinate=None):
    self.pixel_size = pixel_size
    self.rotation = rotation
    self.coordinate = coordinate

  def get_units_per_pixel(self):
    """Returns the pixel size in map units.

    Returns:
      Two value list.
    """
    xy_ = self.pixel_size
    if self.rotation[0] != 0 or self.rotation[1] != 0:
      xy_[0] = math.sqrt(
        math.pow(self.pixel_size[0], 2) + math.pow(self.rotation[1], 2)
      )
      xy_[1] = math.sqrt(
        math.pow(self.pixel_size[1], 2) + math.pow(self.rotation[0], 2)
      )
    return xy_

class PixelSizeResult:
  """Class for pixel size result.

  Attributes:
      conform: Conform value.
      deviation: Deviation value.
      is_conform: True if pixel size is conform.
      min_size: Min size of the pixel.
      vmin: Conformity min value.
      vmax: Conformity max value.
  """
  def __init__(self, xy_=None, conform=None, deviation=None):
    self.conform = conform
    self.deviation = deviation
    # calculate result
    self.vmin = self.conform * (1 - self.deviation)
    self.vmax = self.conform * (1 + self.deviation)
    self.is_conform = False
    x__, y__ = xy_
    if x__ < 0:
      x__ = -x__
    if y__ < 0:
      y__ = -y__
    if x__ and y__:
      self.is_conform = (
        self.vmin <= x__ <= self.vmax and self.vmin <= y__ <= self.vmax
      )
    self.min_size = x__
    if y__ < x__:
      self.min_size = y__

  def result_row(self):
    """Returns the result row.

    Returns:
      List with values is_conform, min_size, vmin and vmax.
    """
    return [self.is_conform, self.min_size, self.vmin, self.vmax]

class BandsLenResult:
  """Class for bands len result.

  Attributes:
      conform: Conform value.
      deviation: Deviation value.
      is_conform: True if pixel size is conform.
      bands_len: Number of bands.
  """
  def __init__(self, bands_len=None, conform=None, deviation=None):
    self.conform = conform
    self.deviation = deviation
    self.bands_len = bands_len
    # calculate result
    self.is_conform = bands_len == conform

  def result_row(self):
    """Returns the result row.

    Returns:
      List with values is_conform, bands_len.
    """
    return [self.is_conform, self.bands_len]

class DigitalLevelResult:
  """Class for digital level result.

  Attributes:
      conform: Conform value.
      deviation: Deviation value.
      is_conform: True if pixel size is conform.
      bands_dt: Bands GDAL data types.
  """
  def __init__(self, bands_dt=None, conform=None, deviation=None, max_bands=None):
    self.conform = conform
    self.deviation = deviation
    if max_bands is None:
      max_bands = 0
    self.max_bands = max_bands
    self.bands_dl = []
    # calculate result
    self.is_conform = True
    for i__ in range(min(len(bands_dt), self.max_bands)):
      dt_ = bands_dt[i__]
      if dt_ == 1:
        self.bands_dl.append(8)
      elif dt_ in [2, 3, 8]:
        self.bands_dl.append(16)
      elif dt_ in [4, 5, 6, 9, 10]:
        self.bands_dl.append(32)
      elif dt_ in [7, 11]:
        self.bands_dl.append(64)
      else:
        self.bands_dl.append(None)
      self.is_conform &= dt_ == conform

  def result_row(self):
    """Returns the result row.

    Returns:
      List with values is_conform and each band digital level.
    """
    row = [self.is_conform]
    row.append(','.join(map(str, self.bands_dl)))
    return row

class RadBalanceResult:
  """Class for radiometric balance result.

  Attributes:
      conform: Conform value.
      is_conform: True if pixel size is conform.
      bands_stats: Bands statistics for radiometric balance.
  """
  def __init__(self, bands_stats=None, conform=None, saturation=None):
    self.conform = conform
    self.bands_stats = bands_stats
    # calculate result
    saturation = self.conform * 100
    self.is_conform = True
    for stats in bands_stats:
      # stats = [vmin, vmax, rmin, rmax, cmin, cmax, pmin*100, pmax*100]
      self.is_conform &= stats[6] < saturation and stats[7] < saturation

  def result_row(self):
    """Returns the result row.

    Returns:
      List with values is_conform and each band digital level.
    """
    row = [self.is_conform]
    row.append(';'.join([','.join(map(str, stats)) for stats in self.bands_stats]))
    return row
