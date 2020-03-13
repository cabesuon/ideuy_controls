"""Main program for postgis controls.

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
from controls.postgis_controls.enums import Rule
from controls.postgis_controls.pgdb import (
  PGDBManager, PGDBManagerError, PGDBConnection, PGDBCredentials
)
from controls.commons_controls.file import (
  FileManager, FileManagerError, read_json_file
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
      'check if all tables in a schema comply or not with selected rules'
    )
  )
  parser.add_argument('dbname', help=_('database name'))
  parser.add_argument('dbschema', help=_('database schema'))
  parser.add_argument('user', help=_('database user'))
  parser.add_argument('password', help=_('database password'))
  parser.add_argument('output', help=_('output folder'))
  parser.add_argument(
    '--host',
    default='localhost',
    help=_('database host')
  )
  parser.add_argument(
    '--port',
    type=int,
    default=5432,
    help=_('database port')
  )
  parser.add_argument(
    '--rule',
    choices=[
      Rule.invalid.value,
      Rule.duplicate.value,
      Rule.multipart.value,
      Rule.intersect.value,
      Rule.null.value,
      Rule.aall.value
    ],
    default=Rule.aall.value,
    help=_('rule')
  )
  parser.add_argument(
    '--summary',
    default='resumen.txt',
    help=_('summary file name'))
  parser.add_argument(
    '--admissibles',
    help=_('admissible intersections file name'))
  args = parser.parse_args()
  return args

def init_file_manager(out_dir, rule):
  """ Helper function to initialize the file manager, and create output folders.

  Args:
    out_dir: Folder path to output result files.
    rule: Name to create sub folder to output result files.

  Returns:
    A FileManager object to handle all file and folder operations.
  """
  fman = None
  try:
    fman = FileManager(out_dir, '.')
    if rule in (Rule.invalid.value, Rule.aall.value):
      fman.add_dir(Rule.invalid.value)
    if rule in (Rule.duplicate.value, Rule.aall.value):
      fman.add_dir(Rule.duplicate.value)
    if rule in (Rule.multipart.value, Rule.aall.value):
      fman.add_dir(Rule.multipart.value)
    if rule in (Rule.null.value, Rule.aall.value):
      fman.add_dir(Rule.null.value)
    if rule == Rule.intersect.value:
      fman.add_dir(Rule.intersect.value)
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


def init_pgdb(host, port, dbname, username, password):
  """ Helper function to initialize the postgis manager.

  Args:
    host: Host of the DBMS.
    port: Port number of the DBMS.
    dbname: Name of the database.
    username: Name of the user.
    password: Password of the user.

  Returns:
    A PGDBManager object to handle all database operations.
  """
  pgdb = None
  try:
    pgdb = PGDBManager(
      PGDBConnection(host, port, dbname),
      PGDBCredentials(username, password)
    )
    pgdb.connect()
  except PGDBManagerError as err:
    logger.error('%s: %s', _('ERROR'), str(err), exc_info=True)
    pgdb = None
  return pgdb

def init_summary_data(in_params, num_tables, summary_data):
  """ Helper procedure to initialize the summary output file.

  Args:
    in_params: Input parameters to the program.
    num_tables: Number of tables evaluated.
    summary_data: Summary data dictionary.
  """
  summary_data[_('Parameters')] = in_params
  summary_data[_('Number of tables')] = num_tables
  summary_data[Rule.invalid.value] = []
  summary_data[Rule.duplicate.value] = []
  summary_data[Rule.multipart.value] = []
  summary_data[Rule.null.value] = []
  summary_data[Rule.intersect.value] = []

def end_summary_data(tman, summary_data):
  """ Helper procedure to update process start and end time of summary data.

  Args:
    tman: TimeManager object to get start and end times.
    summary_data: Summary data dictionary.
  """
  summary_data[_('Start time')] = tman.dt_start
  summary_data[_('End time')] = tman.dt_end

def process_result(fman, rule, table, data, keys=None):
  """ Helper procedure to write control result to detail output file.

  Args:
    fman: FileManager object to write detail output file.
    rule: Name of the rule.
    table: Name of the table.
    data: Dictionary with the header and rows for the detail output file.
    keys: Keys of row values to write.
  """
  if keys:
    for key in keys:
      if data['rows'][key]:
        fman.write_csv_file(
          rule,
          '{}_{}.csv'.format(table, key),
          data['hrow'],
          data['rows'][key].to_list()
        )
  else:
    fman.write_csv_file(rule, '{}.csv'.format(table), data['hrow'], data['rows'])

def control_table(man, dbi, control, summary_data):
  """Helper procedure to execute a control on a table.

  Args:
    man: Dictionary containing FileManager and PGDBManager instances.
    dbi: Dictionary containing schema, table and tables.
    control: Dictionary containing the rule and the admissibles intersections.
    summary_data: Summary data dictionary.
  """
  if control['rule'] in (Rule.invalid.value, Rule.aall.value):
    invs = man['pgdb'].get_invalid_geoms_from_table(dbi['dbschema'], dbi['table'])
    if invs:
      process_result(
        man['fman'],
        Rule.invalid.value,
        dbi['table'],
        {
          'hrow': [_('id'), _('reason'), _('location')],
          'rows': [inv.to_list() for inv in invs]
        }
      )
      summary_data[Rule.invalid.value].append(dbi['table'])
  if control['rule'] in (Rule.duplicate.value, Rule.aall.value):
    dups = man['pgdb'].get_duplicate_geoms_from_table(dbi['dbschema'], dbi['table'])
    if dups:
      process_result(
        man['fman'],
        Rule.duplicate.value,
        dbi['table'],
        {
          'hrow': [_('id'), _('amount')],
          'rows': [dup.to_list() for dup in dups]
        }
      )
      summary_data[Rule.duplicate.value].append(dbi['table'])
  if control['rule'] in (Rule.multipart.value, Rule.aall.value):
    muls = man['pgdb'].get_multipart_geoms_from_table(dbi['dbschema'], dbi['table'])
    if muls:
      process_result(
        man['fman'],
        Rule.multipart.value,
        dbi['table'],
        {
          'hrow': [_('id'), _('number')],
          'rows': [mul.to_list() for mul in muls]
        }
      )
      summary_data[Rule.multipart.value].append(dbi['table'])
  if control['rule'] in (Rule.null.value, Rule.aall.value):
    nuls = man['pgdb'].get_null_geoms_from_table(dbi['dbschema'], dbi['table'])
    if nuls:
      process_result(
        man['fman'],
        Rule.null.value,
        dbi['table'],
        {
          'hrow': [_('id')],
          'rows': [nul.to_list() for nul in nuls]
        }
      )
      summary_data[Rule.null.value].append(dbi['table'])
  if control['rule'] == Rule.intersect.value:
    i = dbi['tables'].index(dbi['table']) + 1
    if i < len(dbi['tables']):
      ints = man['pgdb'].get_not_allowed_intersection(
        dbi['dbschema'],
        dbi['table'],
        dbi['tables'][i:],
        control['admissibles']
      )
      if ints:
        process_result(
          man['fman'],
          Rule.intersect.value,
          dbi['table'],
          {
            'hrow': [
              _('table-1'),
              _('table-1-id'),
              _('table-2'),
              _('table-2-id'),
              _('intersection'),
              _('message')
            ],
            'rows': ints
          },
          ['point', 'line', 'polygon', 'collection']
        )
        summary_data[Rule.intersect.value].append(dbi['table'])

def main():
  """Main procedure."""
  init_logging()
  args = get_args()
  fman = init_file_manager(args.output, args.rule)
  if not fman:
    sys.exit()
  pgdb = init_pgdb(
    args.host,
    args.port,
    args.dbname,
    args.user,
    args.password
  )
  if not pgdb:
    sys.exit()
  admissibles = read_json_file(args.admissibles)
  tables = pgdb.get_schema_table_names(args.dbschema)
  tman = TimeManager()
  summary_data = {}
  init_summary_data(' '.join(sys.argv), len(tables), summary_data)
  print('{}...'.format(_('Processing')))
  logger.info('%s...', _('Processing'))
  print('{}...'.format(_('Tables')))
  logger.info('%s:', _('Tables'))
  for table in tables:
    print('  {}'.format(table))
    logger.info('  %s', table)
    control_table(
      {
        'fman':fman,
        'pgdb':pgdb
      },
      {
        'dbschema':args.dbschema,
        'table':table,
        'tables':tables,
      },
      {
        'rule':args.rule,
        'admissibles':admissibles
      },
      summary_data)
  tman.end()
  end_summary_data(tman, summary_data)
  fman.write_txt_file(args.summary, summary_data)
  print('{}.'.format(_('End')))
  logger.info('%s.', _('End'))

if __name__ == '__main__':
  main()
