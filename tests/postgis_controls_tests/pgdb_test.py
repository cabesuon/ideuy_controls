"""Module that contains the unit tests for controls.postgis_controls.pgdb.

Examples:
  $python -m unittest pgdb_test.py

Classes:
  TestPGDBManager.
  TestPGDBFunctions.
"""
import unittest

from controls.postgis_controls.pgdb import (
  invalid_geoms_query, duplicate_geoms_query, multipart_geoms_query, null_geoms_query,
  point_in_geojson_geom, intersection_query, PGDBManager, PGDBConnection, PGDBCredentials
)

class TestPGDBManager(unittest.TestCase):
  """Class to manage unit test of PGDBManager methods.

  Attributes:
      pgdb: PGDBManager instance.
  """
  def setUp(self):
    self.pgdb = PGDBManager(
      PGDBConnection('local-data-server', 5432, 'test_vector_db'),
      PGDBCredentials('test_user', 'test_password')
    )

  def test_connect(self):
    """Unit test of PGDBManager method connect."""
    self.pgdb.connect()
    self.assertIsNotNone(self.pgdb.conn)
    self.assertIsNotNone(self.pgdb.cursor)

  def test_get_query_result(self):
    """Unit test of PGDBManager method get_query_result."""
    self.pgdb.connect()
    rows = self.pgdb.get_query_result(
      'SELECT COUNT(*) FROM invalid_geoms.linestrings;'
    )
    self.assertEqual(len(rows), 1)
    self.assertEqual(rows[0][0], 5)
    with self.assertRaises(Exception):
      rows = self.pgdb.get_query_result(
        'SELECT COUNT(*) FROM xxxx.yyyy;'
      )

  def test_get_schema_tables(self):
    """Unit test of PGDBManager method get_schema_tables."""
    self.pgdb.connect()
    actual = self.pgdb.get_schema_table_names('invalid_geoms')
    self.assertEqual(actual, ['linestrings', 'polygons'])
    actual = self.pgdb.get_schema_table_names('public')
    self.assertEqual(actual, [])

  def test_get_invalid_geoms_from_table(self):
    """Unit test of PGDBManager method get_invalid_geoms_from_table."""
    self.pgdb.connect()
    invs = self.pgdb.get_invalid_geoms_from_table('invalid_geoms', 'linestrings')
    actual = [[inv.fid, inv.reason, inv.location] for inv in invs]
    self.assertEqual(
      actual,
      [[5, 'Too few points in geometry component', 'POINT(0 0)']]
    )

  def test_get_duplicate_geoms_from_table(self):
    """Unit test of PGDBManager method get_duplicate_geoms_from_table."""
    self.pgdb.connect()
    dups = self.pgdb.get_duplicate_geoms_from_table('duplicate_geoms', 'points')
    actual = [[dup.fid, dup.number] for dup in dups]
    self.assertEqual(
      actual,
      [[2, 2], [4, 2], [5, 3]]
    )

  def test_get_multipart_geoms_from_table(self):
    """Unit test of PGDBManager method get_multipart_geoms_from_table."""
    self.pgdb.connect()
    muls = self.pgdb.get_multipart_geoms_from_table('multi_geoms', 'points')
    actual = [[mul.fid, mul.number] for mul in muls]
    self.assertEqual(
      actual,
      [[2, 3], [4, 3]]
    )

  def test_get_null_geoms_from_table(self):
    """Unit test of PGDBManager method get_null_geoms_from_table."""
    self.pgdb.connect()
    nuls = self.pgdb.get_null_geoms_from_table('null_geoms', 'points')
    actual = [[nul.fid] for nul in nuls]
    self.assertEqual(
      actual,
      [[2], [4], [5]]
    )

  def test_get_not_allowed_intersection_not_admissible(self):
    """Unit test of PGDBManager method get_not_allowed_intersection, not admissible case."""
    self.pgdb.connect()
    admissibles = {}
    # crosses
    nais = self.pgdb.get_not_allowed_intersection(
      'n_a_i_crosses',
      'linestrings1',
      ['linestrings2'],
      admissibles
    )
    actual = [
      [[nai.table2, nai.fid2, nai.msg] for nai in nais.point],
      [[nai.table2, nai.fid2, nai.msg] for nai in nais.line],
      [[nai.table2, nai.fid2, nai.msg] for nai in nais.polygon],
      [[nai.table2, nai.fid2, nai.msg] for nai in nais.collection]
    ]
    self.assertEqual(
      actual,
      [[['linestrings2', 1, 'not addmissible intersection']], [], [], []]
    )

  def test_get_not_allowed_intersection_crosses(self):
    """Unit test of PGDBManager method get_not_allowed_intersection, cross case."""
    self.pgdb.connect()
    admissibles = {
      'linestrings1': ['linestrings2']
    }
    # crosses
    cros = self.pgdb.get_not_allowed_intersection(
      'n_a_i_crosses',
      'linestrings1',
      ['linestrings2'],
      admissibles
    )
    actual = [
      [[cro.table2, cro.fid2, cro.msg] for cro in cros.point],
      [[cro.table2, cro.fid2, cro.msg] for cro in cros.line],
      [[cro.table2, cro.fid2, cro.msg] for cro in cros.polygon],
      [[cro.table2, cro.fid2, cro.msg] for cro in cros.collection]
    ]
    self.assertEqual(
      actual,
      [[['linestrings2', 1, 'crosses']], [], [], []]
    )

  def test_get_not_allowed_intersection_point_or_line_intersection(self):
    """Unit test of PGDBManager method get_not_allowed_intersection,
    not point or line intersection case.
    """
    self.pgdb.connect()
    # point or line intersection
    admissibles = {
      'polygons2': ['polygons1']
    }
    plis = self.pgdb.get_not_allowed_intersection(
      'n_a_i_int_pto_or_line',
      'polygons2',
      ['polygons1'],
      admissibles
    )
    actual = [
      [[pli.table2, pli.fid2, pli.msg] for pli in plis.point],
      [[pli.table2, pli.fid2, pli.msg] for pli in plis.line],
      [[pli.table2, pli.fid2, pli.msg] for pli in plis.polygon],
      [[pli.table2, pli.fid2, pli.msg] for pli in plis.collection]
    ]
    self.assertEqual(
      actual,
      [
        [],
        [],
        [['polygons1', 1, 'result intersection is not point or line'],
        ['polygons1', 2, 'result intersection is not point or line']],
        []
      ]
    )

  def test_get_not_allowed_intersection_ll_or_lp_intersection(self):
    """Unit test of PGDBManager method get_not_allowed_intersection,
    not line-line or line-point intersection case.
    """
    self.pgdb.connect()
    # point or line intersection
    admissibles = {
      'points': ['polygons1']
    }
    lllpis = self.pgdb.get_not_allowed_intersection(
      'n_a_i_int_pto_or_line',
      'points',
      ['polygons1'],
      admissibles
    )
    actual = [
      [[lllpi.table2, lllpi.fid2, lllpi.msg] for lllpi in lllpis.point],
      [[lllpi.table2, lllpi.fid2, lllpi.msg] for lllpi in lllpis.line],
      [[lllpi.table2, lllpi.fid2, lllpi.msg] for lllpi in lllpis.polygon],
      [[lllpi.table2, lllpi.fid2, lllpi.msg] for lllpi in lllpis.collection]
    ]
    self.assertEqual(
      actual,
      [
        [['polygons1', 1, 'not a line-line or line-polygon intersection']],
        [],
        [],
        []
      ]
    )

  def test_get_not_allowed_intersection_invalid_addmissible_intersection(self):
    """Unit test of PGDBManager method get_not_allowed_intersection, invalid addmisible case."""
    self.pgdb.connect()
    # point or line intersection
    admissibles = {
      'linestrings2': ['polygons1']
    }
    iais = self.pgdb.get_not_allowed_intersection(
      'n_a_i_int_pto_or_line',
      'linestrings2',
      ['polygons1'],
      admissibles
    )
    actual = [
      [[iai.table2, iai.fid2, iai.msg] for iai in iais.point],
      [[iai.table2, iai.fid2, iai.msg] for iai in iais.line],
      [[iai.table2, iai.fid2, iai.msg] for iai in iais.polygon],
      [[iai.table2, iai.fid2, iai.msg] for iai in iais.collection]
    ]
    self.assertEqual(
      actual,
      [
        [],
        [['polygons1', 1, 'invalid addmissible intersection']],
        [],
        []
      ]
    )


class TestPGDBFunctions(unittest.TestCase):
  """Class to manage unit test of pgdb functions."""

  def test_invalid_geoms_query(self):
    """Unit test of function invalid_geoms_query."""
    schema = 'invalid_geoms'
    table = 'linestring'
    expected = (
      'SELECT id, '
      'reason(ST_IsValidDetail(geom)), '
      'ST_AsText(location(ST_IsValidDetail(geom))) '
      'FROM {}.{} '
      'WHERE ST_IsValid(geom) = false '
      'ORDER BY id'
    ).format(schema, table)
    actual = invalid_geoms_query(schema, table)
    self.assertEqual(
      actual,
      expected
    )

  def test_duplicate_geoms_query(self):
    """Unit test of function duplicate_geoms_query."""
    schema = 'duplicate_geoms'
    table = 'points'
    expected = (
      'SELECT id, row '
      'FROM ('
      'SELECT id, ROW_NUMBER() OVER(PARTITION BY geom ORDER BY id asc) AS row '
      'FROM ONLY {}.{} '
      'WHERE geom IS NOT NULL'
      ') dups '
      'WHERE dups.row > 1 '
      'ORDER BY id'
    ).format(schema, table)
    actual = duplicate_geoms_query(schema, table)
    self.assertEqual(
      actual,
      expected
    )

  def test_multipart_geoms_query(self):
    """Unit test of function multipart_geoms_query."""
    schema = 'multipart_geoms'
    table = 'points'
    expected = (
      'SELECT id, ST_NumGeometries(geom) '
      'FROM {}.{} '
      'WHERE ST_NumGeometries(geom) > 1 '
      'ORDER BY id'
    ).format(schema, table)
    actual = multipart_geoms_query(schema, table)
    self.assertEqual(
      actual,
      expected
    )

  def test_null_geoms_query(self):
    """Unit test of function null_geoms_query."""
    schema = 'null_geoms'
    table = 'points'
    expected = (
      'SELECT id '
      'FROM {}.{} '
      'WHERE geom IS NULL '
      'ORDER BY id'
    ).format(schema, table)
    actual = null_geoms_query(schema, table)
    self.assertEqual(
      actual,
      expected
    )

  def test_point_in_geojson_geom(self):
    """Unit test of function point_in_geojson_geom."""
    self.assertTrue(
      point_in_geojson_geom(
        [0, 0],
        {
          'type': 'LineString',
          'coordinates': [[1, 1], [0, 0], [3, 3]]
        }
      )
    )
    self.assertTrue(
      point_in_geojson_geom(
        [0, 0],
        {
          'type': 'Polygon',
          'coordinates': [
            [[3, 3], [0, 3], [0, 0], [3, 0], [3, 3]],
            [[2, 2], [1, 2], [1, 1], [2, 1], [2, 2]]
          ]
        }
      )
    )
    self.assertTrue(
      point_in_geojson_geom(
        [0, 0],
        {
          'type': 'MultiPolygon',
          'coordinates': [[
            [[3, 3], [0, 3], [0, 0], [3, 0], [3, 3]],
            [[2, 2], [1, 2], [1, 1], [2, 1], [2, 2]]
          ]]
        }
      )
    )

  def test_intersection_query(self):
    """Unit test of function intersection_query."""
    schema = 'n_a_i_crosses'
    table1 = 'linestrings1'
    table2 = 'linestrings2'
    expected = (
      'SELECT '
      't1id,'
      't2id,'
      'ST_AsGeoJSON(gi, 3),'
      'ST_AsGeoJSON(g1, 3),'
      'ST_AsGeoJSON(g2, 3),'
      'ST_AsText(ST_Multi(gi)),'
      't1_crosses_t2,'
      'ST_Dimension(gi) '
      'FROM ('
        'SELECT '
        't1.id AS t1id,'
        't2.id AS t2id,'
        't1.geom AS g1,'
        't2.geom AS g2,'
        'ST_Intersection(t1.geom, t2.geom) AS gi,'
        'ST_Crosses(t1.geom, t2.geom) AS t1_crosses_t2 '
        'FROM {0}.{1} AS t1, {0}.{2} AS t2 '
        'WHERE ST_Intersects(t1.geom, t2.geom) AND NOT ST_Touches(t1.geom, t2.geom) '
        'ORDER BY t1.id'
      ') AS foo'
    ).format(schema, table1, table2)
    actual = intersection_query(schema, table1, table2)
    self.assertEqual(
      actual,
      expected
    )
