"""Util module that contains the tools to manage input/output files of a control.

Functions:
  read_json_file.

Classes:
  FileManagerError.
  FileManager.
"""
import os
import errno
import csv
import gettext
import logging
import json

def read_json_file(file_name):
  """Read a JSON file.

  Args:
    file_name: Name of the file.

  Returns:
    JSON object.
  """
  if not file_name:
    return None
  data = None
  if os.path.isfile(file_name):
    with open(file_name) as json_data:
      data = json.load(json_data)
  return data

class FileManagerError(Exception):
  """Exception for FileManager."""

class FileManager:
  """Class to manage input/output files of a control.

  Attributes:
      output_dir: Folder path for output files.
      logger: Logging object.
  """

  def __init__(self, output_dir, logger=None):
    # parameters
    self.output_dir = output_dir
    self.logger = logger or logging.getLogger(__name__)
    # internal
    self._ = gettext.gettext
    # check dirs
    try:
      os.makedirs(self.output_dir)
    except OSError as err:
      if err.errno != errno.EEXIST:
        raise FileExistsError(self._('Cannot create output dir'))

  def add_dir(self, dir_name):
    """Add a new folder to the output folder.

    Args:
      dir_name: Name of the folder to add.

    Returns:
      Full path of added folder.

    Raises:
      FileManagerError
    """
    path = os.path.join(self.output_dir, dir_name)
    try:
      os.makedirs(path)
    except OSError as err:
      if err.errno != errno.EEXIST:
        raise FileManagerError(
          '{}. {}'.format(self._('Cannot add dir'), self._('Folder already exist'))
        )
    return path

  def get_dir(self, dir_name):
    """Return full path of a folder in output folder.

    Args:
      dir_name: Name of the folder.

    Returns:
      Full path of the folder.
    """
    return os.path.join(self.output_dir, dir_name)

  def _output_file_path(self, dir_name, file_name):
    """Helper method to return full path of a file in the output folder.

    Args:
      dir_name: Name of the folder.
      file_name: Name of the file.

    Returns:
      Full path of the file.
    """
    if dir_name:
      return os.path.join(self.get_dir(dir_name), file_name)
    return os.path.join(self.output_dir, file_name)

  def start_csv_file(self, file_name, hrow):
    """Initialize a CSV file with the headers.

    Args:
      file_name: Name of the file.
      hrow: Header of the file.
    """
    with open(self._output_file_path(None, file_name), 'w', newline='') as csvfile:
      writer = csv.writer(csvfile)
      if hrow:
        writer.writerow(hrow)

  def append_csv_file(self, file_name, row):
    """Append a row to a CSV file.

    Args:
      file_name: Name of the file.
      row: Row to append to the file.
    """
    with open(self._output_file_path(None, file_name), 'a', newline='') as csvfile:
      writer = csv.writer(csvfile)
      if row:
        writer.writerow(row)

  def write_csv_file(self, dir_name, file_name, hrow, rows):
    """Write a CSV file to a folder in the output folder.

    Args:
      dir_name: Name of the folder in the output folder.
      file_name: Name of the file.
      hrow: Header of the file.
      rows: Rows of the file.
    """
    with open(
      self._output_file_path(dir_name, file_name),
      'w',
      newline='',
      encoding='utf-8'
      ) as csvfile:
      writer = csv.writer(csvfile)
      if hrow:
        writer.writerow(hrow)
      if rows:
        for row in rows:
          writer.writerow(row)

  def write_txt_file(self, file_name, data):
    """Write a text file to the output folder.

    Args:
      file_name: Name of the file.
      data: Data of the file.
    """
    with open(self._output_file_path(None, file_name), 'w', encoding='utf-8') as txtfile:
      if data:
        for key, val in data.items():
          txtfile.write('{}: {}\n'.format(key, val))
