"""Module that contains the tools to open and retrieve raster properties and statistics.

Functions:

Classes:
  ImgManagerError.
  ImgManager.
"""
import logging
import gettext
import numpy as np
from osgeo import gdal
from controls.imagery_controls.results import WorldFileData

class RasterManagerError(Exception):
  """Exception for RasterManager."""

class RasterManager:
  """Class to open and retrieve raster properties and statistics.

  Attributes:
    conn_params: PGDBConnection instance containing server host, port and database name.
    cred_params: PGDBCredentials instance containing username and password.
    logger: Logging object.
    conn: Connection to database.
    cursor: Cursor of connection to database.
  """

  def __init__(self, raster=None, logger=None):
    # internal
    self._ = gettext.gettext
    # parameters
    self.logger = logger or logging.getLogger(__name__)
    self.raster = raster
    try:
      self.dataset = gdal.Open(self.raster)
    except RuntimeError:
      msg = '{}'.format(self._('Cannot open image'))
      self.logger.error(msg, exc_info=True)
      raise RasterManagerError(msg)
    self.geo_transform = self.dataset.GetGeoTransform()
    self.wfd = WorldFileData(
      pixel_size=[self.geo_transform[1], self.geo_transform[5]],
      rotation=[self.geo_transform[4], self.geo_transform[2]]
    )

  def get_dataset(self):
    """Returns the raster dataset.

    Returns:
      Raster dataset.

    Raises:
      RasterManagerError
    """
    return self.dataset

  def get_raster_band(self, no_):
    """Returns a band of the raster dataset.

    Returns:
      Raster dataset band no_.

    Raises:
      RasterManagerError
    """
    band = None
    try:
      band = self.dataset.GetRasterBand(no_)
    except RuntimeError:
      msg = '{}'.format(self._('Cannot retrieve raster band'))
      self.logger.error(msg, exc_info=True)
      raise RasterManagerError(msg)
    return band

  def get_raster_units_per_pixel(self):
    """Returns the units per pixel (cell size) of the raster.

    Returns:
      Two values list with width and height units.

    Raises:
      RasterManagerError
    """
    return self.wfd.get_units_per_pixel()

  def get_raster_bands_len(self):
    """Returns the number of bands of the raster.

    Returns:
      An integer.

    Raises:
      RasterManagerError
    """
    bands_len = None
    try:
      bands_len = self.dataset.RasterCount
    except RuntimeError:
      msg = '{}'.format(self._('Cannot retrieve raster bands len'))
      self.logger.error(msg, exc_info=True)
      raise RasterManagerError(msg)
    return bands_len

  def get_raster_bands_datatype(self):
    """Returns the data type of the bands of the raster.

    Returns:
      List of integers.

    Raises:
      RasterManagerError
    """
    bands_dt = []
    try:
      for r__ in range(self.dataset.RasterCount):
        band = self.get_raster_band(r__ + 1)
        bands_dt.append(band.DataType)
    except RasterManagerError as err:
      raise err
    except RuntimeError:
      msg = '{}'.format(self._('Cannot retrieve raster bands len'))
      self.logger.error(msg, exc_info=True)
      raise RasterManagerError(msg)
    return bands_dt

  def get_raster_bands_rad_balance(self, deviation):
    """Returns the statistics for the radiometric balace of the bands of the raster.

    Returns:
      List of list of integers.

    Raises:
      RasterManagerError
    """
    bands_stats = []
    try:
      for r__ in range(self.dataset.RasterCount):
        band = self.get_raster_band(r__ + 1)
        stats = band.GetStatistics(True, True)
        vmin = stats[0]
        vmax = stats[1]
        rmin = vmin * (1 + deviation)
        rmax = vmax * (1 - deviation)
        band_arr = band.ReadAsArray(
          0,
          0,
          self.dataset.RasterXSize,
          self.dataset.RasterYSize
        ).astype(np.float)
        cmin = np.count_nonzero(band_arr < rmin)
        cmax = np.count_nonzero(band_arr > rmax)
        cval = self.dataset.RasterXSize * self.dataset.RasterYSize
        pmin = round(cmin/cval, 6)
        pmax = round(cmax/cval, 6)
        bands_stats.append([vmin, vmax, rmin, rmax, cmin, cmax, pmin*100, pmax*100])
    except RasterManagerError as err:
      raise err
    except RuntimeError:
      msg = '{}'.format(self._('Cannot retrieve raster bands len'))
      self.logger.error(msg, exc_info=True)
      raise RasterManagerError(msg)
    return bands_stats
