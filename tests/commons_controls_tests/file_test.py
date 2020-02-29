"""Module that contains the unit tests for controls.commons_controls.file.

Examples:
  $python -m unittest file_test.py

Classes:
  TestFileManager.
  TestFileFunctions.
"""
import unittest
import gettext
import json
import csv
import os
from controls.commons_controls.file import (
  FileManager, read_json_file
)

class TestFileManager(unittest.TestCase):
  """Class to manage unit test of FileManager methods.

  Attributes:
      fman: FileManager instance.
  """
  def setUp(self):
    self._ = gettext.gettext
    self.fman = FileManager(
      '_common-tests-file-test-output-dir_'
    )

  def test_add_dir(self):
    """Unit test of FileManager method add_dir."""
    dir_name = 'dir_name'
    dir_path = self.fman.add_dir(dir_name)
    self.assertTrue(
      os.path.isdir(dir_path),
      self._('dir was not added')
    )

  def test_get_dir(self):
    """Unit test of FileManager method get_dir."""
    dir_name = 'dir_name'
    dir_path = self.fman.get_dir(dir_name)
    self.assertEqual(
      dir_path,
      os.path.join(self.fman.output_dir, dir_name),
      self._('incorrect get_dir return value')
    )

  def test_start_csv_file(self):
    """Unit test of FileManager method start_csv_file."""
    file_name = 'file_name.csv'
    hrow = ['Header A', 'Header B', 'Header C']
    self.fman.start_csv_file(file_name, hrow)
    file_path = os.path.join(self.fman.output_dir, file_name)
    self.assertTrue(
      os.path.isfile(file_path),
      self._('csv file was not created')
    )
    ahrow = []
    with open(file_path, 'r', newline='') as csvfile:
      reader = csv.reader(csvfile)
      ahrow = next(reader)
    self.assertEqual(
      hrow,
      ahrow,
      self._('incorrect csv header')
    )

  def test_append_csv_file(self):
    """Unit test of FileManager method append_csv_file."""
    file_name = 'file_name.csv'
    hrow = ['Header A', 'Header B', 'Header C']
    self.fman.start_csv_file(file_name, hrow)
    file_path = os.path.join(self.fman.output_dir, file_name)
    row = ['1', '1', '1']
    self.fman.append_csv_file(file_name, row)
    with open(file_path, 'r', newline='') as csvfile:
      reader = csv.reader(csvfile)
      next(reader)
      arow = next(reader)
    self.assertEqual(
      row,
      arow,
      self._('incorrect csv row')
    )

  def test_write_csv_file(self):
    """Unit test of FileManager method write_csv_file."""
    file_name = 'file_name.csv'
    hrow = ['Header A', 'Header B', 'Header C']
    rows = [['1', '1', '1'], ['2', '2', '2'], ['3', '3', '3']]
    self.fman.write_csv_file(None, file_name, hrow, rows)
    file_path = os.path.join(self.fman.output_dir, file_name)
    with open(file_path, 'r', newline='') as csvfile:
      reader = csv.reader(csvfile)
      ahrow = next(reader)
      arows = [next(reader), next(reader), next(reader)]
    self.assertEqual(
      hrow,
      ahrow,
      self._('incorrect csv header')
    )
    self.assertEqual(
      rows,
      arows,
      self._('incorrect csv rows')
    )

  def test_write_txt_file(self):
    """Unit test of FileManager method write_txt_file."""
    file_name = 'file_name.txt'
    data = {
      'prop 1': '1',
      'prop 2': '2',
      'prop 3': '3'
    }
    self.fman.write_txt_file(file_name, data)
    file_path = os.path.join(self.fman.output_dir, file_name)
    with open(file_path, 'r', encoding='utf-8') as txtfile:
      text = txtfile.read()
    self.assertEqual(
      'prop 1: 1\nprop 2: 2\nprop 3: 3\n',
      text,
      self._('incorrect text')
    )

class TestFileFunctions(unittest.TestCase):
  """Class to manage unit test of file module functions."""

  def setUp(self):
    self._ = gettext.gettext

  def test_read_json_file(self):
    """Unit test of function read_json_file."""
    file_name = 'file_name.json'
    data = json.dumps({
      'prop 1': '1',
      'prop 2': '2',
      'prop 3': '3'
    })
    with open(file_name, 'w', encoding='utf-8') as jsonfile:
      jsonfile.write(data)
    adata = json.dumps(read_json_file(file_name))
    self.assertEqual(
      data,
      adata,
      self._('incorrect json')
    )
