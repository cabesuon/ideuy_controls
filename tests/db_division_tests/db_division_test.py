"""Module that contains the unit tests for division_bd.py.
Examples:
  $python -m unittest db_division_test.py

"""
import unittest
import sys
import os

# add top level package to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))

from controls.db_division.main import ( # pylint: disable=import-error, C0413
    db_connect, create_consignments_table, convert_consignments_srid, get_consignments,
    create_schema, get_tables_from_original_schema, create_table, load_data
)

class TestDividisionBD(unittest.TestCase):
    """Class to manage unit test of division_bd methods.

    Attributes:
        host: database host
        port: database port
        db: database name
        user: database user
        password: database password
    """
    def setUp(self):
        """Unit test setup."""
        self.host = 'localhost'
        self.port = 5432
        self.db = 'test_db_division'
        self.user = 'test_user'
        self.password = 'test_password'

    def test_db_connect(self):
        """Unit test of db_connection function."""
        conn = db_connect(self.host, self.port, self.db, self.user, self.password)
        self.assertIsNotNone(conn)
        with conn.cursor() as c:
            self.assertIsNotNone(c)

    def test_get_tables_from_original_schema(self):
        """Unit test of get_tables_from_original_schema function."""
        conn = db_connect(self.host, self.port, self.db, self.user, self.password)
        with conn.cursor() as c:
            tables_all = get_tables_from_original_schema(c, 'cartografia_nacional_hidrografia')
            self.assertEqual(tables_all, [('agua_a', ), ('agua_estancada_desconocida_a', ),
                                          ('area_humeda_a', )])

    def test_create_consignments_table(self):
        """Unit test of create_consignments_table procedure."""
        # create table for querying consignments
        conn = db_connect(self.host, self.port, self.db, self.user, self.password)
        with conn.cursor() as c:
            tables_all = get_tables_from_original_schema(c, 'cartografia_nacional_hidrografia')
            sql_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))),
            'controls', 'db_division', 'files', 'Remesa_Nacional.sql')
            create_consignments_table(c, 'public', 'remesa_nacional', sql_file, 'cartografia_nacional_hidrografia', tables_all)
            statement = 'SELECT COUNT(*) FROM public.remesa_nacional;'
            c.execute(statement)
            rows = c.fetchall()
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0][0], 12)

    def test_get_consignments(self):
        """Unit test of create_consignments_table function."""
        conn = db_connect(self.host, self.port, self.db, self.user, self.password)
        with conn.cursor() as c:
            tables_all = get_tables_from_original_schema(c, 'cartografia_nacional_hidrografia')
            sql_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))), 'controls', 'db_division', 'files', 'Remesa_Nacional.sql')
            create_consignments_table(c, 'public', 'remesa_nacional', sql_file, 'cartografia_nacional_hidrografia', tables_all)
            consignments = get_consignments(c, 'public', 'remesa_nacional') 
            self.assertEqual(len(consignments), 12)

    def test_convert_consignments_srid(self):
        """Unit test of convert_consignments_srid procedure."""
        conn = db_connect(self.host, self.port, self.db, self.user, self.password)
        with conn.cursor() as c:
            tables_all = get_tables_from_original_schema(c, 'cartografia_nacional_hidrografia')
            sql_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))), 'controls', 'db_division', 'files', 'Remesa_Nacional.sql')
            create_consignments_table(c, 'public', 'remesa_nacional', sql_file, 'cartografia_nacional_hidrografia', tables_all)
            # change SRID to 5381
            statement = 'ALTER TABLE public.remesa_nacional\
            ALTER COLUMN geom TYPE geometry(MultiPolygon, 5381)\
            USING ST_Transform(geom, 5381);'
            c.execute(statement)
            # checking if SRID whas correctly changed
            statement = "SELECT Find_SRID('public', 'remesa_nacional', 'geom');"
            c.execute(statement)
            rows = c.fetchall()
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0][0], 5381)
            # convert SRID and check
            convert_consignments_srid(c,  'public', 'remesa_nacional', 'cartografia_nacional_hidrografia', tables_all)
            statement = "SELECT Find_SRID('public', 'remesa_nacional', 'geom');"
            c.execute(statement)
            rows = c.fetchall()
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0][0], 31981)

    def test_create_schema(self):
        """Unit test of create_schema function."""
        # create schema for the new consignment - id = rn01
        conn = db_connect(self.host, self.port, self.db, self.user, self.password)
        with conn.cursor() as c:
            # delete schema if exists
            statement = 'DROP SCHEMA IF EXISTS rn01 CASCADE'
            c.execute(statement)
            # create new schema
            consignment_id = 1
            schema_new = create_schema(c, 'public', 'rn', consignment_id)
            statement = "SELECT COUNT(schema_name) FROM information_schema.schemata WHERE schema_name = '" + schema_new + "'"
            c.execute(statement)
            rows = c.fetchall()
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0][0], 1)

    def test_create_table(self):
        """Unit test of create_table procedure."""
        conn = db_connect(self.host, self.port, self.db, self.user, self.password)
        with conn.cursor() as c:
            table_original = 'cartografia_nacional_hidrografia.agua_estancada_desconocida_a'
            table_new = 'rn01.agua_estancada_desconocida_a'
            create_table(c, table_original, table_new)
            statement = "SELECT COUNT(*) FROM information_schema.tables WHERE  table_schema = 'rn01'AND table_name = 'agua_estancada_desconocida_a'"
            c.execute(statement)
            rows = c.fetchall()
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0][0], 1)

    def test_load_data(self):
        """Unit test of load_data procedure."""
        conn = db_connect(self.host, self.port, self.db, self.user, self.password)
        with conn.cursor() as c:
            consignment_id = 1
            table_name = 'agua_estancada_desconocida_a'
            table_original = 'cartografia_nacional_hidrografia.agua_estancada_desconocida_a'
            table_new = 'rn01.agua_estancada_desconocida_a'            
            load_data(c, 'public', 'remesa_nacional', consignment_id, table_name, table_original, table_new)
            statement = "SELECT COUNT(*) FROM rn01.agua_estancada_desconocida_a"
            c.execute(statement)
            rows = c.fetchall()
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0][0], 4455)

if __name__ == "__main__":
    unittest.main()
