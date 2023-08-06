#!/usr/bin/python

"""
Defines the backend connection class for MySQL through the
python-mysql backend databases.
"""

# define authorship information
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = []
__copyright__       = 'Copyright (c) 2011, Projex Software'
__license__         = 'LGPL'

# maintanence information
__maintainer__      = 'Projex Software'
__email__           = 'team@projexsoftware.com'

# define version information (major,minor,maintanence)
__depends__        = ['MySQLdb']
__version_info__   = (0, 0, 0)
__version__        = '%i.%i.%i' % __version_info__

#------------------------------------------------------------------------------

import datetime
import logging
import os.path
import re
import threading

import projex.text
import projex.errors

from orb                 import errors, Orb
from orb.common          import ColumnType
from orb.connection      import Connection
from orb.transaction     import Transaction
from orb.table           import Table
from orb.join            import Join
from orb.query           import Query as Q
from orb.valuemapper     import ValueMapper
from orb.common          import CallbackType

logger = logging.getLogger(__name__)

try:
    import MySQLdb as mysql
    from MySQLdb.cursors import DictCursor
    
except ImportError:
    text = 'For MySQL backend, ensure python-mysql is installed'
    deperr  = projex.errors.DependencyNotFoundError(text)
    logger.debug(deperr)
    mysql = None
    DictCursor = None

#----------------------------------------------------------------------

from orb.backends.sqlbase import SqlBase,\
                                 DEFAULT_SCHEMA_CMDS as SQL_SCHEMA_CMDS,\
                                 DEFAULT_COLUMN_CMDS as SQL_COLUMN_CMDS,\
                                 DEFAULT_TYPE_MAP as SQL_TYPE_MAP,\
                                 SqlColumnEngine

#------------------------------------------------------------------------------

MYSQL_SCHEMA_CMDS = {
'create':
    """
    CREATE TABLE {table} ({columns},{constraints}) ENGINE=InnoDB;
    """,
'create_inherited':
    """
    CREATE {table} (
        {inherit_id} INTEGER NOT NULL REFERENCES {inherits},{columns},{constraints}
    ) ENGINE=InnoDB;
    """,
'exists':
    """
    SHOW TABLES LIKE %(table)s;
    """,
'existing_columns':
    """
    SHOW COLUMNS FROM {table} IN {database};
    """
}
DEFAULT_SCHEMA_CMDS = SQL_SCHEMA_CMDS.copy()
DEFAULT_SCHEMA_CMDS.update(MYSQL_SCHEMA_CMDS)

MYSQL_COLUMN_CMDS = {
'ContainsSensitive': 'COLLATE latin1_general_cs LIKE',
'ContainsInsensitive': 'LIKE',
}
DEFAULT_COLUMN_CMDS = SQL_COLUMN_CMDS.copy()
DEFAULT_COLUMN_CMDS.update(MYSQL_COLUMN_CMDS)


MYSQL_TYPE_MAP = {
}
DEFAULT_TYPE_MAP = SQL_TYPE_MAP.copy()
DEFAULT_TYPE_MAP.update(MYSQL_TYPE_MAP)

#------------------------------------------------------------------------------

class MySQL(SqlBase):
    """ 
    Creates a MySQL backend connection type for handling database
    connections to MySQL databases.
    """
    def __init__(self, database):
        super(MySQL, self).__init__(database,
                                    stringWrapper='`',
                                    schemaCommands=DEFAULT_SCHEMA_CMDS,
                                    columnCommands=DEFAULT_COLUMN_CMDS,
                                    typeMap=DEFAULT_TYPE_MAP)
        
        # update the integer engine with a custom primary command
        int_engine = self.columnEngine(ColumnType.Integer)
        int_engine.setCommand('create_primary', '{column} SERIAL')
        int_engine.setCommand('add_primary', 'ADD COLUMN {column} SERIAL')
    
    #----------------------------------------------------------------------
    #                         PROTECTED METHODS
    #----------------------------------------------------------------------
    def _execute(self, 
                command, 
                data       = None, 
                autoCommit = True,
                autoClose  = True,
                returning  = True,
                mapper     = dict):
        """
        Executes the inputed command into the current \
        connection cursor.
        
        :param      command    | <str>
                    data       | <dict> || None
                    autoCommit | <bool> | commit database changes immediately
                    autoClose  | <bool> | closes connections immediately
        
        :return     [{<str> key: <variant>, ..}, ..]
        """
        if data is None:
            data = {}
            
        # when in debug mode, simply log the command to the logger
        elif self.database().commandsBlocked():
            logger.info(command % data)
            return []
        
        def map_value(command, key, value):
            if type(value) in (list, tuple, set):
                data.pop(key, None)
                mapped_items = []
                for i, subvalue in enumerate(value):
                    new_key = '{0}_{1}'.format(key, i)
                    command, new_items = map_value(command, new_key, subvalue)
                    mapped_items += new_items
                
                subkeys = []
                for subkey, subvalue in mapped_items:
                    subkeys.append('%({0})s'.format(subkey))
                    data[subkey] = subvalue
                
                command = command.replace('%({0})s'.format(key),
                                          '('+','.join(subkeys)+')')
                
                return command, mapped_items
            else:
                data[key] = ValueMapper.mappedValue(value)
                return command, [(key, value)]
        
        for key, value in data.items():
            command, items = map_value(command, key, value)
        
        # create a new cursor for this transaction
        db = self.backendDb()
        if not db:
            raise errors.ConnectionLostError()
        
        cursor = db.cursor()
        cursor._defer_warnings = not self.internalsEnabled()
        get_last_row = 'LAST_INSERT_ID()' in command
        command = command.replace('; SELECT LAST_INSERT_ID()', '')
        
        sql = (command % data)
        logger.debug(sql)
        
        try:
            cursor.execute(command, data)
        
        except mysql.OperationalError, err:
            if err[0] == 1317:
                raise errors.Interruption()
            
            raise
        
        except Exception, err:
            raise
        
        if returning:
            results = map(mapper, cursor.fetchall())
            if not results and get_last_row and cursor.lastrowid:
                results = [{'PRIMARY_KEY': cursor.lastrowid}]
        else:
            results = []
        
        if autoCommit:
            self.commit()
        
        if autoClose:
            cursor.close()
        
        return results
    
    def _open(self, db):
        """
        Opens a new database connection to the datbase defined
        by the inputed database.
        
        :param      db | <orb.Database>
        
        :return     <bool> success
        """
        if not mysql:
            raise errors.MissingBackend('MySQLdb not installed.')
            
        dbname  = db.databaseName()
        user    = db.username()
        pword   = db.password()
        host    = db.host()
        if not host:
            host = 'localhost'
        
        port    = db.port()
        if not port:
            port = 3306
        
        # create the python connection
        try:
            mysqldb = mysql.connect(host=host,
                                    port=port,
                                    user=user,
                                    passwd=pword,
                                    db=dbname)
            mysqldb.cursorclass = DictCursor
            return mysqldb
        
        except mysql.OperationalError, err:
            raise errors.ConnectionError('Could not connect to MySQL', db)
    
    def _interrupt(self, threadId, backendDb):
        """
        Interrupts the given backend database connection from a separate thread.
        
        :param      threadId | <int>
                    backendDb | <variant> | backend specific database.
        """
        backendDb.kill(backendDb.thread_id())
    
    #----------------------------------------------------------------------
    #                       PUBLIC METHODS
    #----------------------------------------------------------------------
    
    def existingColumns(self, schema, namespace=None, mapper=None):
        """
        Looks up the existing columns from the database based on the
        inputed schema and namespace information.
        
        :param      schema      | <orb.TableSchema>
                    namespace   | <str> || None
        
        :return     [<str>, ..]
        """
        if mapper is None:
            mapper = map(lambda x: x['Field'], results)
        
        return super(MySQL, self).existingColumn(schema, namespace, mapper)
    
# register the mysql backend
if mysql:
    Connection.register('MySQL', MySQL)