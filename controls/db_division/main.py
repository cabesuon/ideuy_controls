r""" Database division by consignments.
    This program creates an independent schema for every consigment, inserting only objects
    intersecting with it's geometry.

Parameters:
    $python main.py host port database schema
    user password consignments_sql_file consignments_schema consignments_table
    consignment_schema_prefix

Examples:
    $python main.py -h

    $python main.py localhost 5432 CN_HID_10K_R_01 cartografia_nacional_hidrografia
    postgres postgres files\Remesa_Nacional.sql public remesa_nacional rn

    $python main.py localhost 5432 CN_HID_10K_R_01 cartografia_nacional_hidrografia
    postgres postgres files\sql\Remesa_Urbana.sql public remesa_urbana ru
"""

import sys
import argparse
import logging
import gettext
import psycopg2


# set gettext function
# pylint: enable=wrong-import-position
_ = gettext.gettext # pylint: disable=C0103

# logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__) # pylint: disable=C0103
logging.basicConfig(level=logging.INFO)
logger.setLevel(logging.INFO)


def get_args():
    """ Return arguments from input. """
    parser = argparse.ArgumentParser(description=_('This program creates an independent schema \
    for every consigment, inserting only objects intersecting with its geometry.'))
    parser.add_argument('host', help=_('database host'))
    parser.add_argument('port', help=_('database port'))
    parser.add_argument('database', help=_('database name'))
    parser.add_argument('schema', help=_('schema name'))
    parser.add_argument('user', help=_('database username'))
    parser.add_argument('password', help=_('database password'))
    parser.add_argument('consignments_sql_file',
                        help=_('path to the file with the consignments definitions'))
    parser.add_argument('consignments_schema',
                        help=_('name of the schema that contains the consignments table'))
    parser.add_argument('consignments_table', help=_('name of the consignments table'))
    parser.add_argument('consignments_schema_prefix',
                        help=_('prefix for the schema names to be created for every consignment'))
    return parser.parse_args()

def db_connect(host, port, database, user, password):
    """ Helper function to connect to the database.
    Args:
        host: Host of the DBMS.
        port: Port number of the DBMS.
        database: Name of the database.
        user: Name of the user.
        password: Password of the user.
    Returns:
        A connection object to handle all database operations.
    """
    connection_parameters = {
        'host': host,
        'port': port,
        'database': database,
        'user': user,
        'password': password
    }
    try:
        connection = psycopg2.connect(**connection_parameters)
        connection.autocommit = True
    except:
        logger.error('{}\n{}'.format(_('It is not possible to connect to the database.'),
                                     sys.exc_info()))
        sys.exit()
    return connection

def create_consignments_table(cursor, consignments_schema, consignments_table, sql_file,
                              data_schema, tables_all):
    """ Helper procedure to create the consignments table.
    Args:
        cursor: DB cursor.
        consignments_schema: schema name to be used.
        consignments_table: table name to be created.
        sql_file: sql file with consignments definitions.
        data_schema: schema with the data.
        tables_all: list of all tables names.
    """
    try:
        # delete existing consignments definitions
        statement = 'DROP TABLE IF EXISTS {}.{}'.format(consignments_schema, consignments_table)
        cursor.execute(statement)
        # load consignments definition in the database from sql file
        with open(sql_file, "r") as file:
            cursor.execute(file.read())
        # convert consignments SRID to the SRID used in data
        convert_consignments_srid(cursor, consignments_schema, consignments_table,
                                  data_schema, tables_all)
    except:
        logger.error('{}\n{}'.format(_('It is not possibe to create consignments table.'), sys.exc_info()))
        sys.exit()

def convert_consignments_srid(cursor, consignments_schema, consignments_table, data_schema,
                              tables_all):
    """ Helper procedure to change the consigments definition SRID.
    Args:
        cursor: DB cursor.
        consignments_schema: schema name to be used.
        consignments_table: consingments table name.
        data_schema: schema with the data.
        tables_all: list of all tables names.
    """
    try:
        # get SRID from consignments
        logger.info('{}...'.format(_('Searching for consignments and data SRID.')))
        statement = "SELECT Find_SRID('{}', '{}', 'geom');".format(
            consignments_schema, consignments_table)
        cursor.execute(statement)
        consignments_srid_tmp = cursor.fetchall()
        consignments_srid = consignments_srid_tmp[0][0]
        if consignments_srid <= 0:
            logger.error('{}'.format(_('It is not possible to find the consignments SRID.')))
            sys.exit()
        logger.info('{}: {}'.format(_('consignments SRID'), str(consignments_srid)))
        # get the SRID from data - Checking all tables to be sure that they use the same SRID
        srid = -1
        for table in tables_all:
            statement = "SELECT Find_SRID('" + data_schema + "', '" + table[0] + "', 'geom');"
            cursor.execute(statement)
            result = cursor.fetchall()
            if srid == -1:
                srid = result[0][0]
            elif srid != result[0][0]:
                logger.error('{}'.format(_('Different tables in the same schema uses different SRID.')))
                sys.exit()
        if srid <= 0:
            logger.error('{}'.format(_('It is not possible to find the data SRID.')))
            sys.exit()
        logger.info('{}: {}'.format(_('Data SRID'), str(srid)))
        if consignments_srid != srid:
            # modify the SRID
            logger.info('{} {}.'.format(_('Converting consignments SRID to'), str(srid)))
            statement = 'ALTER TABLE ' + consignments_schema + '.' + consignments_table +'\
                    ALTER COLUMN geom TYPE geometry(MultiPolygon, ' + str(srid) +')\
                    USING ST_Transform(geom, ' + str(srid) +');'
            cursor.execute(statement)
        else:
            logger.info('{}'.format(_('SRID conversions not needed.')))
    except:
        logger.error('{}\n{}'.format(_('It is not possible to convert the consignments SRID to the data SRID.'), sys.exc_info()))
        sys.exit()

def get_consignments(cursor, schema, table):
    """ Helper function to get a list of the consinments.
    Args:
        cursor: DB cursor.
        schema: consginments schema name.
        table: consingments table name.
    Returns:
        A list of all the consignments.
    """
    try:
        cursor.execute('SELECT DISTINCT remesa FROM {}.{} ORDER BY remesa'.format(schema, table))
        return cursor.fetchall()
    except:
        logger.error('{} {}.{}.\n{0}'.format(_('It is not possible to query the table'), schema, table, sys.exc_info()))
        sys.exit()

def create_schema(cursor, consignment_table, consignments_schema_prefix, consignment_id):
    """ Helper function to create a schema.
    Args:
        cursor: DB cursor.
        consignments_table: consingments table name.
        consignments_schema_prefix: prefix to be used in the schema.
        consignment_id: consingments identification.
    Returns:
        Created schema name.
    """
    try:
        schema = '{0}{1:0=2d}'.format(consignments_schema_prefix, consignment_id)
        logger.info('{}: {}'.format(_('Creating schema'), schema))
        statement = 'DROP SCHEMA IF EXISTS {} CASCADE'.format(schema)
        cursor.execute(statement)
        statement = 'CREATE SCHEMA {};'.format(schema)
        cursor.execute(statement)
    except:
        logger.error('{}\n{}'.format(_('It is not possible to create the schema.'), sys.exc_info()))
        sys.exit()
    return schema

def get_tables_from_original_schema(cursor, schema):
    """ Helper function to get a list of the tables.
    Args:
        cursor: DB cursor.
        schema: schema name.
    Returns:
        A list of all data tables.
    """
    try:
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = '" +
                       schema + "' ORDER BY table_name")
        return cursor.fetchall()
    except:
        logger.error('{}\n{}'.format(_('It is not possible to query the original schema tables.'), 
                                     sys.exc_info()))
        sys.exit()

def create_table(cursor, table_src, table_dest):
    """ Helper procedure to create table with the same structure than existing table.
    Args:
        cursor: DB cursor.
        table_src: existing table name.
        table_dest: new table name.
    """
    try:
        statement_create_table = 'CREATE TABLE ' + table_dest + ' ( like ' + table_src + ')'
        cursor.execute(statement_create_table)
    except:
        logger.error('{}\n{}'.format(_('It is not possible to create the table.'), sys.exc_info()))
        sys.exit()

def load_data(cursor, consignments_schema, consignments_table, consignment_id, table_name, table_src, table_dest):
    """ Helper procedure to load intersecting data to a consignment schema.
    Args:
        cursor: DB cursor.
        consignments_schema: consgnments schema name.
        consignments_table: consingments table name.
        consignment_id: consingments identification.
        table_name: table name to be logged.
        table_src: data table name.
        table_dest: schema table name.
    """
    try:
        statement_insert = 'INSERT INTO ' + table_dest +'\
                SELECT DISTINCT cn.* \
                FROM ' + table_src + ' AS cn, ' + consignments_schema + '.' + consignments_table + ' AS r\
                WHERE r.remesa = ' + str(consignment_id) + ' and ST_intersects(cn.geom, r.geom)'
        cursor.execute(statement_insert)
    except:
        logger.error('{}\n{}'.format(_('It is not possible to add data in the table.'), sys.exc_info()))
        sys.exit()
    else:
        if cursor.rowcount > 0:
            logger.info('{} {}: {}...'.format(_('Objects added to the table'), table_name, str(cursor.rowcount)))

def main():
    """Main procedure."""
    # execute logic
    logger.info('{}...'.format(_('Processing')))
    args = get_args()
    # connect to db
    conn = db_connect(args.host, args.port, args.database, args.user, args.password)
    with conn.cursor() as c:
        # get list of tables in the original schema
        tables_all = get_tables_from_original_schema(c, args.schema)
        tables_count = str(len(tables_all))
        # create table for querying consignments
        create_consignments_table(c, args.consignments_schema, args.consignments_table, args.consignments_sql_file, args.schema, tables_all)
        # for every consignment
        for consignment_result in get_consignments(c, args.consignments_schema, args.consignments_table):
            consignment_id = int(consignment_result[0])
            # create schema for the new consignment
            schema_new = create_schema(c, args.consignments_schema, args.consignments_schema_prefix, consignment_id)
            # iterate over the schema tables that contains the objects
            logger.info('{} {} {}.'.format(_('Creating'), tables_count, _('tables')))
            logger.info('{}...'.format(_('Searching objects that intersects with the consignment')))
            for table in tables_all:
                table_original = args.schema + '.' + table[0]
                table_new = schema_new + '.' + table[0]
                # create table
                create_table(c, table_original, table_new)
                # load intersecting objects into the table
                load_data(c, args.consignments_schema, args.consignments_table, consignment_id, table[0], table_original, table_new)
    conn.close()
    logger.info('{}'.format(_('End.')))

if __name__ == '__main__':
    main()
