"""Module that contains the tools to connect and query a PostGIS database.

Functions:
  invalid_geoms_query.
  duplicate_geoms_query.
  multipart_geoms_query.
  null_geoms_query.
  point_in_geojson_geom.
  intersection_query.

Classes:
  InvalidGeomResult.
  DuplicateGeomResult.
  MultipartGeomResult.
  NullGeomResult.
  IntersectGeomResult.
  NotAllowedIntersectionsResult.
  PGDBManagerError.
  PGDBManager.
"""
import uuid
import json
import logging
import gettext
import psycopg2

def invalid_geoms_query(schema, table):
  """Returns sql query to check invalid geometries of a table.

  Args:
    schema: Name of the schema.
    table: Name of the table.

  Returns:
    String sql query.
  """
  return (
    'SELECT id, '
    'reason(ST_IsValidDetail(geom)), '
    'ST_AsText(location(ST_IsValidDetail(geom))) '
    'FROM {}.{} '
    'WHERE ST_IsValid(geom) = false '
    'ORDER BY id'
  ).format(schema, table)

def duplicate_geoms_query(schema, table):
  """ Returns sql query to check duplicate geometries of a table.

  Args:
    schema: Name of the schema.
    table: Name of the table.

  Returns:
    String sql query.
  """
  return (
    'SELECT id, row '
    'FROM ('
    'SELECT id, ROW_NUMBER() OVER(PARTITION BY geom ORDER BY id asc) AS row '
    'FROM ONLY {}.{} '
    'WHERE geom IS NOT NULL'
    ') dups '
    'WHERE dups.row > 1 '
    'ORDER BY id'
  ).format(schema, table)

def multipart_geoms_query(schema, table):
  """Returns sql query to check multipart geometries of a table.

  Args:
    schema: Name of the schema.
    table: Name of the table.

  Returns:
    String sql query.
  """
  return (
    'SELECT id, ST_NumGeometries(geom) '
    'FROM {}.{} '
    'WHERE ST_NumGeometries(geom) > 1 '
    'ORDER BY id'
  ).format(schema, table)

def null_geoms_query(schema, table):
  """Returns sql query to check null geometries of a table.

  Args:
    schema: Name of the schema.
    table: Name of the table.

  Returns:
    String sql query.
  """
  return (
    'SELECT id '
    'FROM {}.{} '
    'WHERE geom IS NULL '
    'ORDER BY id'
  ).format(schema, table)

def point_in_geojson_geom(point, geom):
  """Returns True if point is a point of the geometry.

  Args:
    point: Two elements number list.
    geom: GeoJSON object.

  Returns:
    Boolean.
  """
  if geom['type'] == 'LineString':
    return point in geom['coordinates']
  if geom['type'] == 'Polygon' or geom['type'] == 'MultiLineString':
    for coords in geom['coordinates']:
      if point in coords:
        return True
  if geom['type'] == 'MultiPolygon':
    for pols in geom['coordinates']:
      for coords in pols:
        if point in coords:
          return True
  return False

def intersection_query(schema, table1, table2):
  """Returns sql query to check intersection between two tables.

  Args:
    schema: Name of the schema.
    table1: Name of the first table.
    table2: Name of the second table.

  Returns:
    String sql query.
  """
  return (
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

class InvalidGeomResult:
  """Class for a invalid geometry result.

  Attributes:
      fid: Feature ID.
      reason: Reason for invalidity.
      location: Point where invalidity occurs.
  """
  def __init__(self, fid=None, reason=None, location=None):
    self.fid = fid
    self.reason = reason
    self.location = location

  def from_list(self, arr):
    """Load attribute values from a list.

    Args:
      arr: List with fid, reason, location values.
    """
    self.fid = arr[0]
    self.reason = arr[1]
    self.location = arr[2]

  def to_list(self):
    """Returns the attribute values in a list.

    Returns:
      List with fid, reason, location values.
    """
    return [self.fid, self.reason, self.location]

class DuplicateGeomResult:
  """Class for a duplicate geometry result.

  Attributes:
      fid: Feature ID.
      number: Number of duplications.
  """

  def __init__(self, fid=None, number=None):
    self.fid = fid
    self.number = number

  def from_list(self, arr):
    """Load attribute values from a list.

    Args:
      arr: List with fid, number values.
    """
    self.fid = arr[0]
    self.number = arr[1]

  def to_list(self):
    """Load attribute values from a list.

    Args:
      arr: List with fid, number values.
    """
    return [self.fid, self.number]

class MultipartGeomResult:
  """Class for a multipart geometry result.

  Attributes:
      fid: Feature ID.
      number: Number of duplications.
  """
  def __init__(self, fid=None, number=None):
    self.fid = fid
    self.number = number

  def from_list(self, arr):
    """Load attribute values from a list.

    Args:
      arr: List with fid, number values.
    """
    self.fid = arr[0]
    self.number = arr[1]

  def to_list(self):
    """Load attribute values from a list.

    Args:
      arr: List with fid, number values.
    """
    return [self.fid, self.number]

class NullGeomResult:
  """Class for a null geometry result.

  Attributes:
      fid: Feature ID.
  """

  def __init__(self, fid=None):
    self.fid = fid

  def from_list(self, arr):
    """Load attribute values from a list.

    Args:
      arr: List with fid values.
    """
    self.fid = arr[0]

  def to_list(self):
    """Load attribute values from a list.

    Args:
      arr: List with fid values.
    """
    return [self.fid]

class IntersectGeomResult:
  """Class for a intersection geometry result.

  Attributes:
      fid1: Feature 1 ID.
      table1: Table name of feature 1.
      fid2: Feature 2 ID.
      table2: Table name of feature 2.
      int_geom: Geometry of the intersection.
      msg: Message of invalid intersection.
  """

  def __init__(self, table1=None, fid1=None, table2=None, fid2=None, int_geom=None, msg=None):
    self.table1 = table1
    self.fid1 = fid1
    self.table2 = table2
    self.fid2 = fid2
    self.int_geom = int_geom
    self.msg = msg

  def from_list(self, arr):
    """Load attribute values from a list.

    Args:
      arr: List with fid1, table1, fid2, table2, int_geom, msg values.
    """
    self.table1 = arr[0]
    self.fid1 = arr[1]
    self.table2 = arr[1]
    self.fid2 = arr[2]
    self.int_geom = arr[3]
    self.msg = arr[4]

  def to_list(self):
    """Load attribute values from a list.

    Args:
      arr: List with fid1, table1, fid2, table2, int_geom, msg values.
    """
    return [
      self.table1,
      self.fid1,
      self.table2,
      self.fid2,
      self.int_geom,
      self.msg
    ]

class NotAllowedIntersectionsResult: # pylint: disable=R0903
  """Class for not allowed intersections result.

  Attributes:
    point: Point intersection geometries.
    line: LineString intersection geometries.
    polygon: Polygon intersection geometries.
    collection: Collection intersection geometries.
  """

  def __init__(self, point=None, line=None, polygon=None, collection=None):
    if point is None:
      self.point = []
    else:
      self.point = point
    if line is None:
      self.line = []
    else:
      self.line = line
    if polygon is None:
      self.polygon = []
    else:
      self.polygon = polygon
    if collection is None:
      self.collection = []
    else:
      self.collection = collection

class PGDBManagerError(Exception):
  """Exception for PGDBManager."""

class PGDBConnection: # pylint: disable=R0903
  """Class for postgis database connection parameters.

  Attributes:
    host: Host of the DBMS.
    port: Port number of the DBMS.
    dbname: Name of the database.
  """
  def __init__(
    self,
    host='localhost',
    port=5432,
    dbname=None
    ):
    self.host = host
    self.port = port
    self.dbname = dbname

class PGDBCredentials: # pylint: disable=R0903
  """Class for postgis database credentials.

  Attributes:
    username: Name of the user.
    password: Password of the user.
  """
  def __init__(
    self,
    username='postgres',
    password=None,
    ):
    self.username = username
    self.password = password

class PGDBManager:
  """Class to manage connections and queries to a PostGIS database.

  Attributes:
    conn_params: PGDBConnection instance containing server host, port and database name.
    cred_params: PGDBCredentials instance containing username and password.
    logger: Logging object.
    conn: Connection to database.
    cursor: Cursor of connection to database.
  """

  def __init__(
    self,
    conn_params=None,
    cred_params=None,
    logger=None
    ):
    # parameters
    if conn_params is None:
      self.conn_params = PGDBConnection()
    else:
      self.conn_params = conn_params
    if cred_params is None:
      self.cred_params = PGDBCredentials()
    else:
      self.cred_params = cred_params
    self.logger = logger or logging.getLogger(__name__)
    self.conn = None
    self.cursor = None
    # internal
    self._ = gettext.gettext

  def connect(self):
    """Create a connection to the PostGIS database.

    Raises:
      PGDBManagerError
    """
    connstr = "host='{}' port='{}' dbname='{}' user='{}' password='{}'"\
    .format(
      self.conn_params.host,
      self.conn_params.port,
      self.conn_params.dbname,
      self.cred_params.username,
      self.cred_params.password
    )
    try:
      self.conn = psycopg2.connect(connstr)
      self.cursor = self.conn.cursor()
    except:
      self.conn = None
      self.cursor = None
      msg = '{} {}'.format(self._('Cannot connect to database'), self.conn_params.dbname)
      self.logger.error(msg, exc_info=True)
      raise PGDBManagerError(msg)

  def get_query_result(self, query):
    """Execute a query and return the result.

    Args:
      query: SQL string query.

    Returns:
      Row list result of the query.

    Raises:
      PGDBManagerError
    """
    sp_ = uuid.uuid1().hex
    self.cursor.execute('SAVEPOINT "{}"'.format(sp_))
    try:
      self.cursor.execute(query)
      rows = self.cursor.fetchall()
    except Exception:
      self.cursor.execute('ROLLBACK TO SAVEPOINT "{}"'.format(sp_))
      raise
    else:
      self.cursor.execute('RELEASE SAVEPOINT "{}"'.format(sp_))
    return rows

  def get_schema_table_names(self, schema):
    """Return a list with the table names in the schema.

    Args:
      schema: Name of schema.

    Returns:
      String list with table names of the schema.

    Raises:
      PGDBManagerError
    """
    query = (
      'SELECT tablename '
      'FROM pg_tables '
      "WHERE schemaname='{}' "
      'ORDER BY tablename'
    ).format(schema)
    try:
      rows = [row[0] for row in self.get_query_result(query)]
    except:
      msg = '{} {}'.format(self._('Cannot retrieve table names from schema'), schema)
      self.logger.error(msg, exc_info=True)
      raise PGDBManagerError(msg)
    return rows

  def get_invalid_geoms_from_table(self, schema, table):
    """Return a list with invalid geometries result.

    Args:
      schema: Name of schema.
      table: Name of table.

    Returns:
      InvalidGeomResult list.

    Raises:
      PGDBManagerError
    """
    query = invalid_geoms_query(schema, table)
    try:
      rows = self.get_query_result(query)
    except:
      msg = '{} {}.{}'.format(
        self._('Cannot retrieve features with invalid geometries from table'),
        schema,
        table
      )
      self.logger.error(msg, exc_info=True)
      raise PGDBManagerError(msg)
    return [InvalidGeomResult(row[0], row[1], row[2]) for row in rows]

  def get_duplicate_geoms_from_table(self, schema, table):
    """Return a list with duplicate geometries result.

    Args:
      schema: Name of schema.
      table: Name of table.

    Returns:
      DuplicateGeomResult list.

    Raises:
      PGDBManagerError
    """
    query = duplicate_geoms_query(schema, table)
    try:
      rows = self.get_query_result(query)
    except:
      msg = '{} {}.{}'.format(
        self._('Cannot retrieve  features with duplicate geometries from table'),
        schema,
        table
      )
      self.logger.error(msg, exc_info=True)
      raise PGDBManagerError(msg)
    return [DuplicateGeomResult(row[0], row[1]) for row in rows]

  def get_multipart_geoms_from_table(self, schema, table):
    """Return a list with multipart geometries result.

    Args:
      schema: Name of schema.
      table: Name of table.

    Returns:
      MultipartGeomResult list.

    Raises:
      PGDBManagerError
    """
    query = multipart_geoms_query(schema, table)
    try:
      rows = self.get_query_result(query)
    except:
      msg = '{} {}.{}'.format(
        self._('Cannot retrieve features with multipart geometries from table'),
        schema,
        table
      )
      self.logger.error(msg, exc_info=True)
      raise PGDBManagerError(msg)
    return [MultipartGeomResult(row[0], row[1]) for row in rows]

  def get_null_geoms_from_table(self, schema, table):
    """Return a list with null geometries result.

    Args:
      schema: Name of schema.
      table: Name of table.

    Returns:
      NullGeomResult list.

    Raises:
      PGDBManagerError
    """
    query = null_geoms_query(schema, table)
    try:
      rows = self.get_query_result(query)
    except:
      msg = '{} {}.{}'.format(
        self._('Cannot retrieve features with null geometries from table'),
        schema,
        table
      )
      self.logger.error(msg, exc_info=True)
      raise PGDBManagerError(msg)
    return [NullGeomResult(row[0]) for row in rows]

  def _not_allowed_intersection_check(self, table, table2, row, admissibles):
    """Return a string with the not allowed intersection casuistic.

    Args:
      table: Name of table.
      table2: Name of table.
      row: Result of the query.
      admissibles: Admissibles intersections dictionary.

    Returns:
      String message with the not allowed intersection casuistic
    """
    # check if intersection is not admissible
    if not admissibles or table not in admissibles or table2 not in admissibles[table]:
      return self._('not addmissible intersection')
    # check if intersection is a cross
    if row[6]:
      return self._('crosses')
    # check if intersection is not point and not line
    geomi = json.loads(row[2])
    if geomi['type'] != 'Point' and geomi['type'] != 'LineString':
      return self._('result intersection is not point or line')
    points = []
    if geomi['type'] == 'Point':
      points = [geomi['coordinates']]
    else:
      points = [geomi['coordinates'][0], geomi['coordinates'][len(geomi['coordinates'])-1]]
    geom1 = json.loads(row[3])
    geom2 = json.loads(row[4])
    # check if is line-line or line-polygon intersection
    if (
      geom1['type'] in ['LineString', 'MultiLineString']
      and
      geom2['type'] in ['LineString', 'MultiLineString']
    ) or\
    (
      geom1['type'] in ['LineString', 'MultiLineString']
      and
      geom2['type'] in ['Polygon', 'MultiPolygon']
    ) or\
    (
      geom1['type'] in ['Polygon', 'MultiPolygon']
      and
      geom2['type'] in ['LineString', 'MultiLineString']
    ):
      ptoi = 0
      while ptoi < len(points) and\
        (
          point_in_geojson_geom(points[ptoi], geom1)
          or
          point_in_geojson_geom(points[ptoi], geom2)
        ):
        ptoi += 1
      if ptoi == len(points):
        return self._('invalid addmissible intersection')
    return self._('not a line-line or line-polygon intersection')

  def get_not_allowed_intersection(self, schema, table, tables, admissibles):
    """Return a list with not allowed intersection geometries result.

    Args:
      schema: Name of schema.
      table: Name of table.
      tables: Name of tables.
      admissibles: Admissibles intersections dictionary.

    Returns:
      NotAllowedIntersectionsResult list.

    Raises:
      PGDBManagerError
    """
    values = NotAllowedIntersectionsResult(point=[], line=[], polygon=[], collection=[])
    for table2 in tables:
      query = intersection_query(schema, table, table2)
      self.logger.debug(
        '%s: %s - %s', self._('Intersection'), table, table2
      )
      try:
        rows = self.get_query_result(query)
      except PGDBManagerError:
        msg = '{0} {1}.{2} {1}.{3}'.format(
          self._('Cannot retrieve intersection geometries between tables'),
          schema,
          table,
          table2
        )
        self.logger.error(msg, exc_info=True)
      for row in rows:
        msg = self._not_allowed_intersection_check(table, table2, row, admissibles)
        if msg:
          value = IntersectGeomResult(table, row[0], table2, row[1], row[5], msg)
          geomi = json.loads(row[2])
          if geomi['type'] == 'GeometryCollection':
            values.collection.append(value)
          else:
            if row[7] == 0:
              values.point.append(value)
            elif row[7] == 1:
              values.line.append(value)
            else:
              values.polygon.append(value)
    return values
