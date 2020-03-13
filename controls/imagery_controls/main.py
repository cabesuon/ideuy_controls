"""Main program for image controls.

Examples:
  $python main.py -h.
  $python main.py test_vector_db invalid_geoms test_user test_password output
  --host local-data-server --rule invalid.
  $python main.py test_vector_db duplicate_geoms test_user test_password output
  --host local-data-server --rule duplicate.
  $python main.py test_vector_db multipart_geoms test_user test_password output
  --host local-data-server --rule multipart.
  $python main.py test_vector_db null_geoms test_user test_password output
  --host local-data-server --rule null.
"""
import os
import sys
import argparse
import gettext
import logging
# add top level package to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
#pylint: disable=wrong-import-position
from controls.imagery_controls.enums import Control
from controls.imagery_controls.raster import (
  RasterManager, RasterManagerError
)
from controls.imagery_controls.results import (
  WorldFileData, PixelSizeResult, BandsLenResult, DigitalLevelResult, RadBalanceResult
)
from controls.commons_controls.file import (
  FileManager, FileManagerError, read_twf_file, get_files_path
)
from controls.commons_controls.time import TimeManager, get_str_time
#pylint: enable=wrong-import-position
_ = gettext.gettext
# logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__) # pylint: disable=C0103

def get_args():
  """ Return arguments from input. """
  parser = argparse.ArgumentParser(
    description=_(
      'check if all images in a schema comply or not with selected rules'
    )
  )
  parser.add_argument('input', help=_('input folder'))
  parser.add_argument('output', help=_('output folder'))
  parser.add_argument(
    '--control',
    choices=[
      Control.pixel_size.value,
      Control.bands_len.value,
      Control.dig_level.value,
      Control.rad_balance.value,
      Control.srid.value,
      Control.nodata.value,
      Control.aall.value
    ],
    default=Control.aall.value,
    help=_('control')
  )
  parser.add_argument(
    '--conform',
    type=float,
    default=None,
    help=_('conform value')
  )
  parser.add_argument(
    '--deviation',
    type=float,
    default=None,
    help=_('deviation value')
  )
  parser.add_argument(
    '--detail',
    default='detail.csv',
    help=_('detail file name'))
  parser.add_argument(
    '--summary',
    default='summary.txt',
    help=_('summary file name'))
  parser.add_argument(
    '--max_bands',
    type=int,
    default=0,
    help=_('maximun number of bands to control (default all)'))
  parser.add_argument(
    '--recursive',
    dest='recursive',
    action='store_true',
    help='check subfolders'
  )
  parser.add_argument(
    '--non-recursive',
    dest='recursive',
    action='store_false',
    help='do not check subfolders (default)'
  )
  parser.set_defaults(recursive=False)
  # pixel size parameters
  parser.add_argument(
    '--twf',
    type=bool,
    default=False,
    help=_('use twf file, when exist, first (default False)'))
  # return arguments
  args = parser.parse_args()
  return args

def init_file_manager(out_dir, control):
  """ Helper function to initialize the file manager, and create output folders.

  Args:
    out_dir: Folder path to output result file1s.
    control: Name to create sub folder to output result files.

  Returns:
    A FileManager object to handle all file and folder operations.
  """
  fman = None
  try:
    fman = FileManager(out_dir, '.')
    if control in (Control.pixel_size.value, Control.aall.value):
      fman.add_dir(Control.pixel_size.value)
    if control in (Control.bands_len.value, Control.aall.value):
      fman.add_dir(Control.bands_len.value)
    if control in (Control.dig_level.value, Control.aall.value):
      fman.add_dir(Control.dig_level.value)
    if control in (Control.rad_balance.value, Control.aall.value):
      fman.add_dir(Control.rad_balance.value)
    if control in (Control.srid.value, Control.aall.value):
      fman.add_dir(Control.srid.value)
    if control in (Control.nodata.value, Control.aall.value):
      fman.add_dir(Control.nodata.value)
  except FileManagerError as err:
    logger.error('%s: %s', _('ERROR'), str(err), exc_info=True)
    fman = None
  return fman

def init_logging():
  """ Helper function to initialize logging."""
  logger.setLevel(logging.INFO)
  # create a file handler
  handler = logging.FileHandler('{}.log'.format(get_str_time()))
  handler.setLevel(logging.INFO)
  # create a logging format
  formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  handler.setFormatter(formatter)
  # add the file handler to the logger
  logger.addHandler(handler)

def init_detail_file(fman, detail, control):
  """ Helper function to initialize the detail output file.

  Args:
    fman: FileManager instance.
    detail: Detail output file name.
    control: Control name.
  """
  controls = []
  hrows = []
  if control in [Control.pixel_size.value, Control.aall.value]:
    controls.append(Control.pixel_size.value)
    hrows.append([
      _('name'),
      _('conform'),
      _('pixel'),
      _('vmin'),
      _('vmax')
    ])
  elif control in [Control.bands_len.value, Control.aall.value]:
    controls.append(Control.bands_len.value)
    hrows.append([
      _('name'),
      _('conform'),
      _('bands')
    ])
  elif control in [Control.dig_level.value, Control.aall.value]:
    controls.append(Control.dig_level.value)
    hrows.append([
      _('name'),
      _('conform'),
      _('bands')
    ])
  elif control in [Control.rad_balance.value, Control.aall.value]:
    controls.append(Control.rad_balance.value)
    hrows.append([
      _('name'),
      _('conform'),
      _('bands')
    ])
  try:
    for i__, __ in enumerate(controls):
      fman.start_csv_file('{}.csv'.format(detail), hrows[i__], dir_name=controls[i__])
  except FileManagerError as err:
    logger.error('%s: %s', _('ERROR'), str(err), exc_info=True)

def init_summary_data(in_params, num_images, summary_data):
  """ Helper procedure to initialize the summary output file.

  Args:
    in_params: Input parameters to the program.
    num_tables: Number of tables evaluated.
    summary_data: Summary data dictionary.
  """
  summary_data[_('Parameters')] = in_params
  summary_data[_('Number of images')] = num_images
  summary_data[Control.pixel_size.value] = []
  summary_data[Control.bands_len.value] = []
  summary_data[Control.dig_level.value] = []
  summary_data[Control.rad_balance.value] = []
  summary_data[Control.srid.value] = []
  summary_data[Control.nodata.value] = []

def end_summary_data(tman, summary_data):
  """ Helper procedure to update process start and end time of summary data.

  Args:
    tman: TimeManager object to get start and end times.
    summary_data: Summary data dictionary.
  """
  summary_data[_('Start time')] = tman.dt_start
  summary_data[_('End time')] = tman.dt_end

def save_result(fman, name, control, data):
  """ Helper procedure to write control result to detail output file.

  Args:
    fman: FileManager object to write detail output file.
    name: Detail file name.
    control: Name of the control.
    data: Dictionary with the header and rows for the detail output file.
  """
  fman.append_csv_file('{}.csv'.format(name), data, control)

def control_img(fman, img, args, summary_data):
  """Helper procedure to execute a control on a image.

  Args:
    fman: Dictionary containing FileManager instance.
    img: image file path.
    control: Dictionary containing the name and parameters of the control.
    summary_data: Summary data dictionary.
  """
  try:
    raster = RasterManager(img)
  except RasterManagerError as err:
    logger.error('%s', str(err), exc_info=True)
    return
  # pixel size
  if args.control in (Control.pixel_size.value, Control.aall.value):
    xy_ = None
    if args.twf:
      arr = read_twf_file('{}.tfw'.format(img[:-4]))
      if arr:
        wfd = WorldFileData(
          [arr[0], arr[4]],
          [arr[1], arr[3]],
          [arr[2], arr[5]],
        )
        xy_ = wfd.get_units_per_pixel()
      else:
        logger.info('%s.', _('No tfw file'))
    if xy_ is not None:
      xy_ = raster.get_raster_units_per_pixel()
    res = PixelSizeResult(xy_, args.conform, args.deviation)
    row = [img]
    row.extend(res.result_row())
    save_result(
      fman,
      args.detail,
      args.control,
      row
    )
    if not res.is_conform:
      summary_data[args.control].append(img)
  # bands len
  elif args.control in (Control.bands_len.value, Control.aall.value):
    bands_len = raster.get_raster_bands_len()
    res = BandsLenResult(bands_len, args.conform)
    row = [img]
    row.extend(res.result_row())
    save_result(
      fman,
      args.detail,
      args.control,
      row
    )
    if not res.is_conform:
      summary_data[args.control].append(img)
  # digital level
  elif args.control in (Control.dig_level.value, Control.aall.value):
    bands_dt = raster.get_raster_bands_datatype()
    res = DigitalLevelResult(bands_dt, args.conform)
    row = [img]
    row.extend(res.result_row())
    save_result(
      fman,
      args.detail,
      args.control,
      row
    )
    if not res.is_conform:
      summary_data[args.control].append(img)
  # radiometric balance
  elif args.control in (Control.rad_balance.value, Control.aall.value):
    bands_stats = raster.get_raster_bands_rad_balance(args.deviation)
    res = RadBalanceResult(bands_stats, args.conform, args.saturation)
    row = [img]
    row.extend(res.result_row())
    save_result(
      fman,
      args.detail,
      args.control,
      row
    )
    if not res.is_conform:
      summary_data[args.control].append(img)

def main():
  """Main procedure."""
  init_logging()
  args = get_args()
  fman = init_file_manager(args.output, args.control)
  if not fman:
    sys.exit()
  imgs = get_files_path(args.input, 'tif', args.recursive)
  tman = TimeManager()
  summary_data = {}
  init_summary_data(' '.join(sys.argv), len(imgs), summary_data)
  print('{}...'.format(_('Processing')))
  logger.info('%s...', _('Processing'))
  print('{}...'.format(_('Image')))
  logger.info('%s:', _('Image'))
  init_detail_file(fman, args.detail, args.control)
  for img in imgs:
    print('  {}'.format(img))
    logger.info('  %s', img)
    control_img(fman, img, args, summary_data)
  tman.end()
  end_summary_data(tman, summary_data)
  fman.write_txt_file(args.summary, summary_data)
  print('{}.'.format(_('End')))
  logger.info('%s.', _('End'))

if __name__ == '__main__':
  main()
