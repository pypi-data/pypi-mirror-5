#!/usr/bin/python

""" 
Defines the main Table class that will be used when developing
database classes.
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

#------------------------------------------------------------------------------
import datetime
import logging
import re

import projex.text
import projex.rest

from projex.enum        import enum
from projex             import security
from projex.decorators  import abstractmethod

import orb

from orb.caching     import RecordCache, DataCache
from orb.tablebase   import TableBase
from orb.common      import RemovedAction, SearchMode, ColumnType
from orb._orb        import Orb
from orb.query       import Query as Q
from orb             import errors
from orb.valuemapper import ValueMapper

logger = logging.getLogger(__name__)

TEMPLATE_PATTERN = re.compile('\[([^\]:]+[^\]]*)\]')

# treat unicode warnings as errors
from exceptions import UnicodeWarning
from warnings import filterwarnings
filterwarnings(action='error', category=UnicodeWarning)

#------------------------------------------------------------------------------

class Table(object):
    """ 
    Defines the base class type that all database records should inherit from.
    """
    # define the table meta class
    __metaclass__       = TableBase
    
    # meta database information
    __db__              = ''         # name of DB in Environment for this model
    __db_group__        = 'Default'  # name of database group
    __db_name__         = ''         # name of database schema
    __db_tablename__    = ''         # name of table in database
    __db_schema__       = None       # <TableSchema> for direct creation
    __db_ignore__       = True       # bypass database table processing
    
    ReloadOptions = enum('Conflicts',
                         'Modified',
                         'Unmodified',
                         'IgnoreConflicts')
    
    @classmethod
    def __syncdatabase__( cls ):
        """
        This method will be called after all creation and updating syncing
        is called for a database sync.  It will allow a developer to specify
        default information for their class type.
        """
        pass
    
    def __format__(self, format_spec):
        """
        Formats this record based on the inputed format_spec.  If no spec
        is supplied, this is the same as calling str(record).
        
        :param      format_spec | <str>
        
        :return     <str>
        """
        if not format_spec:
            return str(self)
        
        if format_spec == 'primaryKey':
            return str(self.primaryKey())
        else:
            column = self.schema().column(format_spec)
            if column:
                return str(self.recordValue(format_spec))
        
        return super(Table, self).__format__(format_spec)
    
    def __str__(self):
        """
        Defines the custom string format for this table.
        """
        schema = self.schema()
        sform  = ''
        adv    = False
        orb_   = Orb.instance()
        
        # extract any inherited 
        while not sform and schema:
            sform  = schema.stringFormat()
            adv    = schema.useAdvancedFormatting()
            
            if not sform:
                schema = orb_.schema(schema.inherits())
            else:
                break
        
        # use the advanced formatting
        if adv and sform:
            try:
                return sform.format(self, self=self)
            except:
                pass
        
        # use the old-syntax formatting
        elif sform:
            try:
                return sform % self.recordValues()
            except KeyError:
                pass
        
        return super(Table, self).__str__()
    
    def __eq__(self, other):
        """
        Checks to see if the two records are equal to each other
        by comparing their primary key information.
        
        :param      other       <variant>
        
        :return     <bool>
        """
        return id(self) == id(other) or hash(self) == hash(other)
    
    def __ne__(self, other):
        """
        Returns whether or not this object is not equal to the other object.
        
        :param      other | <variant>
        
        :return     <bool>
        """
        return not self.__eq__(other)
    
    def __hash__(self):
        """
        Creates a hash key for this instance based on its primary key info.
        
        :return     <int>
        """
        # use the base id information
        if not self.isRecord():
            return super(Table, self).__hash__()
        
        # return a combination of its table and its primary key hashes
        return hash((self.__class__, self.database(), self.primaryKey()))
    
    def __cmp__(self, other):
        """
        Compares one record to another.
        
        :param      other | <variant>
        
        :return     -1 || 0 || 1
        """
        return cmp(str(self), str(other))
    
    def __init__(self, *args, **kwds):
        """
        Initializes a database record for the table class.  A
        table model can be initialized in a few ways.  Passing
        no arguments will create a fresh record that does not
        exist in the database.  Providing keyword arguments will
        map to this table's schema column name information, 
        setting default values for the record.  Suppling an 
        argument will be the records unique primary key, and 
        trigger a lookup from the database for the record directly.
        
        :param      *args       <tuple> primary key
        :param      **kwds      <dict>  column default values
        """
        # define table properties in a way that shouldn't be accidentally
        # overwritten
        self.__record_defaults      = {}
        self.__record_values        = {}
        self.__record_dbloaded      = set()
        self.__record_datacache     = None
        self.__record_database      = db = kwds.pop('db', None)
        self.__record_namespace     = namespace = kwds.pop('recordNamespace',
                                                           None)
        
        # initialize the defaults
        if 'db_dict' in kwds:
            self._updateFromDatabase(kwds.pop('db_dict'))
        
        elif not args:
            self.initRecord()
            self.resetRecord()
        
        # initialize from the database
        else:
            # extract the primary key for initializing from a record
            if len(args) == 1 and Table.recordcheck(args[0]):
                record  = args[0]
                args    = record.primaryKey()
                values  = record.recordValues().copy()
                self._updateFromDatabase(values)
            
            elif len(args) == 1:
                args = args[0]
            
            data = self.selectFirst(where=Q(type(self)) == args,
                                    limit=1,
                                    db=db,
                                    namespace=namespace,
                                    inflated=False)
            if data:
                self._updateFromDatabase(data)
        
        self.setRecordValues(**kwds)
    
    #----------------------------------------------------------------------
    #                       PROTECTED METHODS
    #----------------------------------------------------------------------
    def _markAsLoaded(self, database=None, columns=None):
        """
        Goes through and marks all the columns as loaded from the database.
        
        :param      columns | [<str>, ..] || None
        """
        if columns is None:
            columns = self.schema().columnNames(includeProxies=False)
        
        for column in columns:
            self.__record_defaults[column] = self.__record_values.get(column)
        
        self.__record_database = database
        self.__record_dbloaded.update(columns)
        
    def _updateFromDatabase(self, values):
        """
        Called from the backend class when it needs to
        manipulate information on this record instance.
        
        :param      values      { <str> key: <variant>, .. }
        """
        schema       = self.schema()
        tableName    = schema.tableName()
        dvalues      = {}
        
        for key, value in values.items():
            if key == 'PRIMARY_KEY':
                primary = self.schema().primaryColumns()
                if not type(value) in (list, tuple):
                    value = (value,)
                if len(primary) != len(value):
                    errors.InvalidPrimaryKeyError(primary, value)
                    continue
                
                for i, col in enumerate(primary):
                    dvalues[col.name()] = value[i]
                    self.__record_dbloaded.add(col.name())
                continue
                
            try:
                tname, colname = key.split('.')
            except ValueError:
                colname = key
                tname = tableName
            
            # value being set for another table from a join
            if tname != tableName:
                continue
            
            column = schema.column(colname)
            if not column:
                continue
            
            dvalues[column.name()] = value
            self.__record_dbloaded.add(colname)
            
        # pylint: disable-msg=W0142
        self.__record_values.update(dvalues)
        self.__record_defaults.update(dvalues)
        
    def _removedFromDatabase( self ):
        """
        Called after a record has been removed from the
        database, so the record instance can clean up
        any additional information.
        """
        self.__record_defaults.clear()
        self.__record_dbloaded.clear()
    
    #----------------------------------------------------------------------
    #                       PRIVATE METHODS
    #----------------------------------------------------------------------
    def changeset(self, columns=None, recurse=True, includeProxies=False):
        """
        Returns a dictionary of changees that have been made 
        to the data from this record.
        
        :return     { <fieldName>: ( <variant> old, <variant> new), .. }
        """
        changes = {}
        is_record = self.isRecord()
        
        for column in self.schema().columns(recurse=recurse,
                                            includeProxies=includeProxies,
                                            include=columns):
            columnName      = column.name()
            newValue        = self.__record_values.get(columnName)
            
            # assume all changes for a new record
            if not is_record:
                oldValue = None
                
                # ignore read only columns for initial insert
                if column.isReadOnly():
                    continue
                
            # only look for changes from loaded columns
            elif columnName in self.__record_dbloaded:
                oldValue = self.__record_defaults.get(columnName)
            
            # otherwise, ignore the change
            else:
                continue
            
            # compare two datetimes
            if isinstance(newValue, datetime.datetime) and \
               isinstance(oldValue, datetime.datetime):
                try:
                    equals = newValue == oldValue
                
                # compare against non timezoned values
                except TypeError:
                    norm_new = newValue.replace(tzinfo=None)
                    norm_old = oldValue.replace(tzinfo=None)
                    equals = norm_new == norm_old
            
            # compare all other types
            else:
                if isinstance(newValue, basestring) and \
                   isinstance(oldValue, basestring):
                    a = projex.text.encoded(newValue)
                    b = projex.text.encoded(oldValue)
                else:
                    a = newValue
                    b = oldValue
                
                try:
                    equals = a == b
                except UnicodeWarning:
                    equals = False
            
            if Table.recordcheck(newValue) and not Table.recordcheck(oldValue):
                equals = newValue.primaryKey() == oldValue
            
            if not equals:
                changes[columnName] = (oldValue, newValue)
            
        return changes
    
    def clearCustomCache(self):
        """
        Clears out any custom cached data.  This is a pure virutal method,
        as by default the Table class does not define any direct custom
        cache information.  Overload this method to wipe any local data that
        is cached when the system decides to clear.
        """
        pass
    
    def commit(self, *args, **kwds):
        """
        Commits the current change set information to the database,
        or inserts this object as a new record into the database.
        This method will only update the database if the record
        has any local changes to it, otherwise, no commit will
        take place.  If the dryRun flag is set, then the SQL
        will be logged but not executed.
        
        :note       From version 0.6.0 on, this method now accepts a mutable
                    keyword dictionary of values.  You can supply any member 
                    value for either the <orb.LookupOptions> or
                    <orb.DatabaseOptions>, 'options' for 
                    an instance of the <orb.DatabaseOptions>
        
        :return     (<str> commit type, <dict> changeset) || None
        """
        # support columns as defined by a variable list of arguments
        if args:
            columns = set(kwds.get('columns', []))
            columns.update(args)
            kwds['columns'] = list(columns)
            
        # grab the database
        db = kwds.pop('db', self.database())
        if not db:
            logger.error('No database defined for %s, cannot commit', str(self))
            return ('error', 'No database defined for {}'.format(self))
        
        # grab the backend
        backend = db.backend()
        if not backend:
            logger.error('No backend found for %s, cannot commit', str(db))
            return ('error', 'No backend for {}'.format(db))
        
        # sync the record to the database
        lookup = kwds.get('lookup', orb.LookupOptions(**kwds))
        options = kwds.get('options', orb.DatabaseOptions(**kwds))
        try:
            results = backend.syncRecord(self, lookup, options)
        except errors.OrbError, err:
            if options.throwErrors:
                raise
            else:
                logger.debug('Failed to commit record.\n%s', err)
                results = {'error': str(err)}
        
        if results and not 'error' in results:
            # clear the cache on changes
            cache = self.recordCache()
            if cache:
                cache.clear()
            
            # clear the index caches
            for index in self.schema().indexes():
                index.clearCache()
            
            # clear any custom caches
            self.clearCustomCache()
        
        return results
    
    def conflicts(self, *columnNames):
        """
        Looks up conflicts from the database by comparing values for specific
        (or all) columns from the database against the local default and 
        value list.  The returned value will be a dictionary containing the
        conflicted column as the key, and a tuple containing the database
        value and the local value cache.  This method is useful to validate
        data being committed to the database won't conflict with what was
        stored when the record was generated.
        
        :sa         reload
        
        :param      columnNames | <varg> [<str> columnName, ..]
        
        :return     {<orb.Column>: (<var> db value, <var> local value, ..)
        """
        if not self.isRecord():
            return {}
        
        schema = self.schema()
        if not columnNames:
            columnNames = schema.columnNames()
        
        query = Q(type(self)) == self
        values = self.selectFirst(columns=columnNames,
                                  where=query,
                                  inflated=False)
        
        # look for clashing changes
        conflicts = {}
        for colname, d_value in values.items():
            # don't care about non-loaded columns
            if not colname in self.__record_dbloaded:
                continue
            
            m_default = self.__record_defaults[colname]
            m_value = self.__record_values[colname]
            
            # always do a primary key comparison since we won't be inflated
            # values from the database
            if Table.recordcheck(m_value):
                m_value = m_value.primaryKey()
            if Table.recordcheck(m_default):
                m_default = m_default.primaryKey()
            
            # ignore unchanged values, we can update without issue
            if m_value == m_default:
                continue
            
            # ignore unchaged values from the database, we can save without
            # conflict
            elif d_value in (m_default, m_value):
                continue
            
            # otherwise, mark the conflict
            conflicts[colname] = (d_value, m_value)
        
        return conflicts
     
    def database(self):
        """
        Returns the database instance for this record.  If no \
        specific datbase is defined, then the database will be looked up \
        based on the name, environment, and current settings from the current \
        Orb manager.
        
        :return     <Database> || None
        """
        if self.__record_database is None:
            self.__record_database = self.getDatabase()
        return self.__record_database
    
    def dataCache(self):
        """
        Returns the cache instance record for this record.
        
        :return     <DataCache>
        """
        if not self.__record_datacache:
            self.__record_datacache = DataCache()
        return self.__record_datacache
    
    def duplicate(self):
        """
        Creates a new record based on this instance, initializing
        it with the data from this record.
        
        :return     <Table>
        """
        db_values = self.__record_values.copy()
        
        for key in self.primaryKeyDict():
            db_values.pop(key, None)
        
        output = self.__class__()
        output.__record_values = db_values
        return output
    
    def findAllRelatedRecords(self):
        """
        Looks up all related records to this record via all the relations
        within the database that would point back to this instance.
        
        :return     [<orb.Table>, ..]
        """
        # lookup cascading removal
        relations = Orb.instance().findRelations(self.schema())
        output = []
        for table, columns in relations:
            for column in columns:
                q = Q(column.name()) == record
                output += table.select(where = q).all()
        return output
    
    def initRecord(self):
        """
        Initializes the default values for this record.
        """
        for column in self.schema().columns(includeProxies=False):
            key = column.name()
            self.__record_defaults[key] = column.default(resolve=True)
    
    def isModified(self):
        """
        Returns whether or not any data has been modified for
        this object.
        
        :return     <bool>
        """
        if not self.isRecord():
            return True
        
        return len(self.changeset()) > 0
    
    def isRecord(self, db=None):
        """
        Returns whether or not this database table record exists
        in the database.
        
        :return     <bool>
        """
        if db is None or db == self.database():
            return self.primaryKey() is not None
        return False
    
    def primaryKey(self):
        """
        Returns the values for the primary key for this record.
        It is important to note, that this will return the column
        values as they are in the database, not as they are on the
        class instance.
        
        :return     <variant> | will return a tuple or column value
        
        :usage      |>>> # this is just an example, not a provided class
                    |>>> from somemodule import Person
                    |>>> p = Person('Eric','Hulser')
                    |>>> p.isRecord()
                    |True
                    |>>> [ col.name() for col in p.schema().primaryColumns() ]
                    |['firstName','lastName']
                    |>>> p.primaryKey()
                    |('Eric','Hulser')
                    |>>> p.setLastName('Smith')
                    |>>> # accessing the column reflects the data on the object
                    |>>> p.firstName(), p.lastName()
                    |('Eric','Smith')
                    |>>> # accessing the pkey reflects the data in the db
                    |>>> p.primaryKey()
                    |('Eric','Hulser')
                    |>>> # committing to the db will update the database,
                    |>>> # and on success, update the object record
                    |>>> p.commit()
                    |{'updated',{'lastName': ('Hulser','Smith')})
                    |>>> # now that the changes are in the DB, the pkey is
                    |>>> # updated to reflect the record
                    |>>> p.primaryKey()
                    |('Eric','Smith')
        """
        cols = self.schema().primaryColumns()
        defaults = self.__record_defaults
        output = []
        for col in cols:
            if not col.name() in self.__record_dbloaded:
                return None
            
            output.append(defaults.get(col.name()))
        
        if len(output) == 1:
            return output[0]
        return tuple(output)
    
    def primaryKeyTuple(self):
        """
        Returns this records primary key as a tuple.
        
        :return     (<variant>, ..)
        """
        cols     = self.schema().primaryColumns()
        defaults = self.__record_defaults
        return tuple([defaults.get(col.name()) for col in cols])
    
    def primaryKeyDict(self):
        """
        Returns a dictionary of the primary key information for this
        record.
        
        :return     <dict>
        """
        cols     = self.schema().primaryColumns()
        defaults = self.__record_defaults
        return dict([(col.name(), defaults.get(col.name())) for col in cols])
    
    def recordNamespace(self):
        """
        Returns the records specific namespace.  This can be used to override
        particular settings for a record.
        
        :return     <str>
        """
        if not self.__record_namespace:
            return self.schema().namespace()
        return self.__record_namespace
    
    def recordValue(self,
                    columnName,
                    default=None,
                    autoInflate=True,
                    useMethod=True):
        """
        Returns the value for the column for this record.
        
        :param      columnName  | <str>
                    default     | <variant>
                    autoInflate | <bool>
        
        :return     <variant>
        """
        columnName = str(columnName)
        
        # lookup the specific column for this instance
        column = self.schema().column(columnName)
        if not column:
            raise errors.ColumnNotFoundWarning(columnName)
        
        elif useMethod:
            method = getattr(self.__class__, column.getterName(), None)
            try:
                orb_getter = type(method.im_func).__name__ == 'gettermethod'
            except AttributeError:
                orb_getter = False
            
            if method is not None and not orb_getter:
                return method(self)
        
        try:
            value = self.__record_values[columnName]
        except KeyError:
            proxy = self.proxyColumn(columnName)
            if proxy and proxy.getter():
                return proxy.getter()(self)
            return default
        
        # return none output's and non-auto inflated values immediately
        if value is None or not (column.isReference() and autoInflate):
            return column.restoreValue(value)
        
        # ensure we have a proper reference model
        refmodel = column.referenceModel()
        if refmodel is None:
           raise errors.TableNotFoundError(column.reference())
        
        # make sure our value already meets the criteria
        elif refmodel.recordcheck(value):
            return value
        
        # inflate the value to the class value
        inst = refmodel.selectFirst(where=Q(refmodel) == value,
                                    db=self.database())
        if value == self.__record_defaults.get(columnName):
            self.__record_defaults[columnName] = inst
        
        # cache the record value
        self.__record_values[columnName] = inst
        return inst
    
    def recordValues(self,
                     columns=None,
                     useFieldNames=False,
                     autoInflate=False,
                     ignorePrimary=False,
                     includeProxies=True,
                     includeAggregates=True,
                     includeJoined=True,
                     recurse=True,
                     mapper=None):
        """
        Returns a dictionary grouping the columns and their
        current values.  If useFieldNames is set to true, then the keys
        for the returned dictionary will be the field name rather than the
        API name for the column.  If the autoInflate value is set to True,
        then you will receive any foreign keys as inflated classes (if you
        have any values that are already inflated in your class, then you
        will still get back the class and not the primary key value).  Setting
        the mapper option will map the value by calling the mapper method.
        
        :param      useFieldNames | <bool>
                    autoInflate | <bool>
                    mapper | <callable> || None
        
        :return     { <str> key: <variant>, .. }
        """
        output = {}
        schema = self.schema()
        for column in self.schema().columns(includeProxies=includeProxies,
                                            includeAggregates=includeAggregates,
                                            includeJoined=includeJoined,
                                            recurse=recurse):
            column_name = column.name()
            if columns is not None and not column_name in columns:
                continue
            
            if ignorePrimary and column.primary():
                continue
            
            if useFieldNames:
                column_name = column.fieldName()
            
            value = self.recordValue(column_name, autoInflate=autoInflate)
            
            if mapper:
                value = mapper(value)
            
            output[column_name] = value
        
        return output
    
    def reload(self, *columnNames, **kwds):
        """
        Reloads specific columns from the database for this record.  This will
        replace both the default and value for this table, so any local cache
        will be replaced.  The returned dictionary will contain a set of
        conflicts from the database.  The key will be the column that is
        conflicting, and the value will be a tuple containing the database
        value and the local value.
        
        :param      columnNames | <varg> (<str> columnName, ..)
                    options     | <Table.ReloadOptions>
        
        :return     {<orb.Column>: (<var> db value, <var> local value, ..)
        """
        opts = Table.ReloadOptions
        reload_options = kwds.get('options',
                                  Table.ReloadOptions.IgnoreConflicts)
       
        if not self.isRecord():
            return {}
        
        if not columnNames:
            columnNames = self.schema().columnNames()
        
        columnNames = list(columnNames)
        
        # only update unmodified columns
        if reload_options & (opts.Modified | opts.Unmodified):
            for colname in self.__record_values:
                m_value = self.__record_values[colname]
                m_default = self.__record_defaults[colname]
                
                if reload_options & opts.Unmodified and m_value != m_default:
                    try:
                        columnNames.remove(colname)
                    except ValueError:
                        continue
                
                elif reload_options & opts.Modified and m_value == m_default:
                    try:
                        columnNames.remove(colname)
                    except ValueError:
                        continue
        
        # don't look anything up if there are no values
        if not columnNames:
            return {}
        
        query = Q(type(self)) == self
        values = self.selectFirst(columns=columnNames,
                                  where=query,
                                  inflated=False)
        
        # look for clashing changes
        conflicts = {}
        for colname, d_value in values.items():
            # don't care about non-loaded columns
            if not colname in self.__record_dbloaded:
                if reload_options & opts.Conflicts:
                    values.pop(colname)
                continue
            
            m_default = self.__record_defaults[colname]
            m_value = self.__record_values[colname]
            
            # ignore unchanged values, we can update without issue
            if m_value == m_default:
                if reload_options & opts.Conflicts:
                    values.pop(colname)
                continue
            
            # ignore unchaged values from the database, we can save without
            # conflict
            elif d_value == m_default:
                if reload_options & opts.Conflicts:
                    values.pop(colname)
                continue
            
            # otherwise, mark the conflict
            conflicts[colname] = (d_value, m_value)
            
            if reload_options & opts.IgnoreConflicts:
                values.pop(colname)
        
        # update the record internals
        self.__record_dbloaded.update(values.keys())
        self.__record_defaults.update(values)
        self.__record_values.update(values)
        
        return conflicts
    
    def remove(self, **kwds):
        """
        Removes this record from the database.  If the dryRun \
        flag is specified then the command will be logged and \
        not executed.
        
        :note       From version 0.6.0 on, this method now accepts a mutable
                    keyword dictionary of values.  You can supply any member 
                    value for either the <orb.LookupOptions> or
                    <orb.DatabaseOptions>, as well as the keyword 'lookup' to 
                    an instance of <orb.LookupOptions> and 'options' for 
                    an instance of the <orb.DatabaseOptions>
        
        :return     <int>
        """
        return orb.RecordSet([self]).remove(**kwds)
    
    def resetRecord(self):
        """
        Resets the values for this record to the database
        defaults.  This will only reset to the local cache, not reload from
        the datbase itself.  To reset the record from database values, 
        use the reload method.
        
        :sa     reload
        """
        self.__record_values = self.__record_defaults.copy()
    
    @abstractmethod
    def retire(self):
        """
        Generic method to "retire" a record.  Each record will handle retirement
        differently, so the system only provides the removal framework for it, 
        but does not support a generic retirement system.  To use this, subclass
        the Table class and implement the retirement method.
        
        :return     <int> | numer of records retired
        """
        return 0
    
    def setDatabase(self, database):
        """
        Sets the specific database instance that this
        record will be using when executing transactions.
        
        :param      database        <Database> || None
        """
        self.__record_database = database
    
    def setRecordDefault(self, columnName, value):
        """
        Sets the default value for the column name at the given value.
        
        :param      columnName | <str>
                    value      | <variant>
        
        :return     <bool> | success
        """
        if not columnName in self.__record_defaults:
            # lookup the proxy column
            proxy = self.proxyColumn(columnName)
            if proxy and proxy.setter():
                proxy.setter()(self, value)
                return True
            
            return False
        
        column = self.schema().column(columnName)
        value = column.storeValue(value)
        
        self.__record_defaults[columnName] = value
        self.__record_values[columnName] = value
        return True
    
    def setRecordValue(self, columnName, value, useMethod=True):
        """
        Sets the value for this record at the inputed column
        name.  If the columnName provided doesn't exist within
        the schema, then the ColumnNotFoundWarning error will be 
        raised.
        
        :param      columnName      <str>
        :param      value           <variant>
        
        :return     <bool> changed
        """
        # convert the inputed value information
        value = ValueMapper.mappedValue(value)
        
        # validate the column
        column = self.schema().column(columnName)
        if not column:
            raise errors.ColumnNotFoundWarning(column)
        
        # set a proxy value
        proxy = self.proxyColumn(columnName)
        if proxy and proxy.setter():
            result = proxy.setter()(self, value)
            if result is not None:
                return result
            return True
        
        elif proxy:
            raise errors.ColumnReadOnlyError(column)
        
        elif useMethod:
            method = getattr(self.__class__, column.setterName(), None)
            try:
                orb_setter = type(method.im_func).__name__ == 'settermethod'
            except AttributeError:
                orb_setter = False
            
            if method is not None and not orb_setter:
                return method(self, value)
        
        # cannot update aggregate or join columns
        if column.isReadOnly():
            raise errors.ColumnReadOnlyError(column)
        
        value = column.storeValue(value)
        
        # make sure we're not changning information
        curr_value = self.__record_values.get(column.name())
        
        # assume when we cannot compare unicodes, they are unequal
        try:
            equals = curr_value == value
        except UnicodeWarning:
            equals = False
        
        if equals or \
           (column.isEncrypted() and curr_value == security.encrypt(value)):
            return False
        
        # make sure the inputed value matches the validation
        validator = column.validator()
        if validator and value is not None and not validator.match(value):
            raise errors.ValidationError(column, value)
        
        self.__record_values[column.name()] = value
        return True
    
    def setRecordValues(self, **data):
        """
        Sets the values for this record from the inputed column
        value pairing
        
        :param      **data      key/value pair for column names
        
        :return     <int> number set
        """
        schema = self.schema()
        count = 0
        for colname, value in data.items():
            col = schema.column(colname)
            if not col:
                continue
            
            try:
                changed = self.setRecordValue(col.name(), value)
            except errors.OrbError:
                continue
            
            if changed:
                count += 1
        return count
    
    def setRecordNamespace(self, namespace):
        """
        Sets the namespace that will be used by this record in the database.
        If no namespace is defined, then it will inherit from its table settings.
        
        :param      namespace | <str> || None
        """
        self.__record_namespace = namespace
    
    def revert(self, *columnNames, **kwds):
        """
        Reverts all conflicting column data from the database so that the
        local modifictaions are up to date with what is in the database.
        
        :sa         reload
        
        :param      columnNames | <varg> [<str> columnName, ..]
                    options     | <Table.ReloadOptions>
        """
        kwds.setdefault('options', Table.ReloadOptions.Conflicts)
        self.reload(*columnNames, **kwds)
    
    def updateFromRecord(self, record):
        """
        Updates this records values from the inputed record.
        
        :param      record | <orb.Table>
        """
        changes = record.changeset()
        for column, values in changes.items():
            try:
                self.setRecordValue(column, values[1])
            except errors.OrbError:
                pass
    
    def validateRecord(self):
        """
        Validates the current records values against its columns.
        
        :return     (<bool> valid, <str> message)
        """
        return self.validateValues(self.recordValues())
    
    def validateValues(self, values):
        """
        Validates the values for the various columns of this record against
        the inputed list of values.
        
        :param      values | {<str> columnName: <variant> value, ..}
        
        :return     (<bool> valid, <str> message)
        """
        success = True
        msg = []
        
        schema = self.schema()
        
        # validate the columns
        for columnName, value in values.items():
            column = schema.column(columnName)
            if ( not column ):
                success = False
                msg.append('%s is not a valid column.' % columnName)
            
            else:
                valid, col_msg = column.validate(value)
                if ( not valid ):
                    success = False
                    msg.append(col_msg)
            
        return (success, '\n\n'.join(msg))
    
    #----------------------------------------------------------------------
    #                           CLASS METHODS
    #----------------------------------------------------------------------
    
    @classmethod
    def defineProxy(cls, typ, getter, setter=None, **options):
        """
        Defines a new proxy column.  Proxy columns are code based properties -
        the information will be generated by methods and not stored directly in
        the databse, however can be referenced abstractly as though they are
        columns.  This is useful for generating things like joined or calculated
        column information.
        
        :param      columnName | <str>
                    getter     | <callable>
                    setter     | <callable>
        """
        proxies = getattr(cls, '_%s__proxies' % cls.__name__, {})
        
        name = options.get('name', getter.__name__)
        
        options['getter'] = getter
        options['setter'] = setter
        options['proxy']  = True
        options['schema'] = cls.schema()
        
        col = orb.Column(typ, name, **options)
        
        proxies[name] = col
        setattr(cls, '_%s__proxies' % cls.__name__, proxies)
    
    @classmethod
    def defineRecord(cls, **kwds):
        """
        Defines a new record for the given class based on the
        inputed set of keywords.  If a record already exists for
        the query, the first found record is returned, otherwise
        a new record is created and returned.
        
        :param      **kwds | columns & values
        """
        # require at least some arguments to be set
        if not kwds:
            return cls()
        
        # lookup the record from the database
        q = Q()
        for key, value in kwds.items():
            q &= Q(key) == value
        
        record = cls.select(where = q).first()
        if not record:
            record = cls(**kwds)
            record.commit()
        
        return record
        
    @classmethod
    def buildSearchQuery(cls, 
                         terms, 
                         mode=SearchMode.All, 
                         additionalColumns=None):
        """
        Generates a search query for the given set of terms based on the given
        terms and join mode.  This method can be overloaded to define custom
        searching values, and is used by the <orb.RecordSet> class to filter
        records.
        
        :usage      |>>> from my_api import MyTable
                    |>>> MyTable.select().search('keywords')
        
        :sa         orb.RecordSet.search
        
        :param      terms   | [<str>, ..]
                    mode    | <orb.SearchMode>
        
        :return     <orb.Query>
        """
        query  = Q()
        schema = cls.schema()
        if ( not schema ):
            return query
        
        search_cols = schema.searchableColumns()
        
        if additionalColumns is not None:
            search_cols += additionalColumns
        
        for search_term in terms:
            term_query = Q()
            for search_col in search_cols:
                model = search_col.schema().model()
                q = Q(model, search_col.name()).contains(search_term)
                term_query |= q
            
            if ( mode == SearchMode.All ):
                query &= term_query
            else:
                query |= term_query
        
        return query
    
    @classmethod
    def baseTableQuery(cls):
        """
        Returns the default query value for the inputed class.  The default
        table query can be used to globally control queries run through a 
        Table's API to always contain a default.  Common cases are when
        filtering out inactive results or user based results.
        
        :return     <orb.Query> || None
        """
        return getattr(cls, '_%s__baseTableQuery' % cls.__name__, None)
    
    @classmethod
    def dictify(cls,
                records,
                useFieldNames=False,
                autoInflate=False,
                mapper=None):
        """
        Converts the inputed records of this table to dictionary values.
        
        :sa         Table.recordValues
        
        :param      records         | <orb.RecordSet> || <list>
                    useFieldNames   | <bool>
                    autoInflate     | <bool>
                    mapper          | <callable> || None
        
        :return     [{<key>: <value>, ..}, ]
        """
        dicter = lambda x: x.recordValues(useFieldNames=useFieldNames,
                                          autoInflate=autoInflate,
                                          mapper=mapper)
        
        return map(dicter, records)
    
    @classmethod
    def getDatabase(cls):
        """
        Returns the database instance for this class.
        
        :return     <Database> || None
        """
        if cls.__db__:
            return orb.Orb.instance().database(cls.__db__)
        else:
            return cls.schema().database()
    
    @classmethod
    def inflateRecord(cls, values, default=None, db=None):
        """
        Returns a new record instance for the given class with the values
        defined from the database.
        
        :param      cls     | <subclass of orb.Table>
                    values  | <dict> values
        
        :return     <orb.Table>
        """
        # inflate values from the database into the given class type
        if Table.recordcheck(values):
            record = values
            values = values._Table__record_values
        else:
            record = None
        
        schema = cls.schema()
        column = schema.polymorphicColumn()
        
        # attept to expand the class to its defined polymorphic type
        if column and column.name() in values:
            morph = column.referenceModel()
            if morph:
                morph_name = str(morph(values[column.name()], db=db))
                dbname = cls.schema().databaseName()
                morph_cls = orb.Orb.instance().model(morph_name,
                                                     database=dbname)
                
                if morph_cls and morph_cls != cls:
                    pcols = morph_cls.schema().primaryColumns()
                    pkeys = []
                    for pcol in pcols:
                        pkeys.append(values.get(pcol.name()))
                    
                    record = morph_cls(*pkeys, db=db)
        
        if record is None:
            record = cls(db_dict=values, db=db)
        
        return record
    
    @classmethod
    def jsonify(cls, 
                records, 
                useFieldNames=False, 
                autoInflate=False, 
                mapper=None):
        """
        Converts the inputed records of this table to json format.
        
        :sa         Table.dictify
        
        :param      records         | <orb.RecordSet> || <list>
                    useFieldNames   | <bool>
                    autoInflate     | <bool>
                    mapper          | <callable> || None
        
        :return     <str> json data
        """
        # convert the data to a string if nothing else to jsonify successfully
        if mapper is None:
            mapper = str
        
        return projex.rest.jsonify(cls.dictify(records, 
                                               useFieldNames=useFieldNames,
                                               autoInflate=autoInflate,
                                               mapper=mapper))
    
    @classmethod
    def proxyColumn(cls, name):
        """
        Returns a column that is treated as a proxy for this widget.
        
        :param      name | <str>
        
        :return     <orb.Column> || None
        """
        return getattr(cls, '_%s__proxies' % cls.__name__, {}).get(str(name))
    
    @classmethod
    def proxyColumns(cls):
        """
        Returns a dictionary of proxy columns for this class type.  Proxy
        columns are dynamic methods that can be treated as common columns of
        data.
        
        :return     {<str> columnName: <orb.Column>, ..}
        """
        return getattr(cls, '_%s__proxies' % cls.__name__, {}).values()
    
    @classmethod
    def popRecordCache(cls):
        """
        Pops the last cache instance from the table.
        
        :return     <orb.RecordCache> || None
        """
        stack = getattr(cls, '_%s__recordCacheStack' % cls.__name__, [])
        if stack:
            return stack.pop()
        return None
    
    @classmethod
    def pushRecordCache(cls, cache):
        """
        Pushes a caching class onto the stack for this table.
        
        :param      cache | <orb.RecordCache>
        """
        stack = getattr(cls, '_%s__recordCacheStack' % cls.__name__, None)
        if stack is None:
            stack = []
            setattr(cls, '_%s__recordCacheStack' % cls.__name__, stack)
        
        stack.append(cache)
    
    @classmethod
    def recordCache(cls):
        """
        Returns the record cache for the inputed class.  If the given class 
        schema does not define caching, then a None valu3e is returned, otherwise
        a RecordCache instance is returned.
        
        :return     <orb.RecordCache> || None
        """
        stack = getattr(cls, '_%s__recordCacheStack' % cls.__name__, [])
        if stack:
            return stack[-1]
        
        # checks to see if the schema defines a cache
        schema = cls.schema()
        if not schema.isCacheEnabled():
            return None
        
        # define the cache for the first time
        cache = RecordCache(cls)
        cache.setExpires(cls, schema.cacheExpireIn())
        cls.pushRecordCache(cache)
        
        # pre-load the records for this cache
        if schema.preloadCache():
            cache.preload(cls)
        
        return cache
    
    @classmethod
    def resolveQueryValue(cls, value):
        """
        Allows for class-level definitions for creating custom query options.
        
        :param      value | <variant>
        
        :return     <variant>
        """
        return value
    
    @classmethod
    def schema(cls):
        """  Returns the class object's schema information. """
        return cls.__db_schema__
    
    @classmethod
    def selectFirst(cls, *args, **kwds):
        """
        Selects records for the class based on the inputed \
        options.  If no db is specified, then the current \
        global database will be used.  If the inflated flag is specified, then \
        the results will be inflated to class instances.  If the flag is left \
        as None, then results will be auto-inflated if no columns were supplied.
        If columns were supplied, then the results will not be inflated by \
        default.
        
        :sa     select
        
        :return     <cls> || None
        """
        return cls.select(*args, **kwds).first()
        
    @classmethod
    def select(cls, *args, **kwds):
        """
        Selects records for the class based on the inputed \
        options.  If no db is specified, then the current \
        global database will be used.  If the inflated flag is specified, then \
        the results will be inflated to class instances.  
        
        If the flag is left as None, then results will be auto-inflated if no 
        columns were supplied.  If columns were supplied, then the results will 
        not be inflated by default.
        
        If the groupBy flag is specified, then the groupBy columns will be added
        to the beginning of the ordered search (to ensure proper paging).  See
        the Table.groupRecords methods for more details.
        
        :note       From version 0.6.0 on, this method now accepts a mutable
                    keyword dictionary of values.  You can supply any member 
                    value for either the <orb.LookupOptions> or
                    <orb.DatabaseOptions>, as well as the keyword 'lookup' to 
                    an instance of <orb.LookupOptions> and 'options' for 
                    an instance of the <orb.DatabaseOptions>
        
        :return     [ <cls>, .. ] || { <variant> grp: <variant> result, .. }
        """
        db = kwds.pop('db', None)
        
        # support legacy code
        arg_headers = ['columns', 'where', 'order', 'limit']
        for i in range(len(args)):
            if ( i == 0 and isinstance(args[i], orb.LookupOptions) ):
                kwds['lookup'] = args[i]
            elif ( i == 1 and isinstance(args[i], orb.DatabaseOptions) ):
                kwds['options'] = args[i]
            else:
                kwds[arg_headers[i]] = args[i]
        
        lookup  = kwds.get('lookup', orb.LookupOptions(**kwds))
        options = kwds.get('options', orb.DatabaseOptions(**kwds))
        
        # setup the default query options
        default_q = cls.baseTableQuery()
        if default_q:
            if lookup.where:
                lookup.where &= default_q
            else:
                lookup.where = default_q
        
        # define the record set and return it
        rset = orb.RecordSet(cls)
        rset.setLookupOptions(lookup)
        rset.setDatabaseOptions(options)
        
        if db is not None:
            rset.setDatabase(db)
        
        return rset
    
    @classmethod
    def setBaseTableQuery(cls, query):
        """
        Sets the default table query value.  This method can be used to control
        all queries for a given table by setting global where inclusions.
        
        :param      query | <orb.Query> || None
        """
        setattr(cls, '_%s__baseTableQuery' % cls.__name__, query)
    
    @classmethod
    def tableSubTypes(cls):
        """
        Returns a list of all the sub-models of this class within the system.
        
        :return     [<subclass of orb.Table>, ..]
        """
        models = orb.Orb.instance().models()
        return [model for model in models if issubclass(model, cls)]
    
    @staticmethod
    def __groupingKey(record, 
                       schema, 
                       grouping, 
                       ref_cache, 
                       autoInflate = False):
        """
        Looks up the grouping key for the inputed record.  If the cache
        value is specified, then it will lookup any reference information within
        the cache and return it.
        
        :param      record | <orb.Table>
                    grouping | <str>
                    cache    | <dict> || None
                    autoInflate | <bool>
        
        :return     <str>
        """
        columnName = grouping
        
        # lookup template patterns
        if ( '[' in columnName ):
            # lookup column patterns
            columnNames = TEMPLATE_PATTERN.findall(columnName)
            syntax      = columnName
        else:
            columnNames = [columnName]
            syntax      = None
    
        column_data = {}
        for columnName in columnNames:
            columnName  = columnName.split(':')[0]
            column      = schema.column(columnName)
            
            if ( not column ):
                logger.warning('%s is not a valid column of %s', 
                               columnName,
                               schema.name())
                continue
            
            # lookup references
            if ( column.isReference() ):
                ref_key = record.recordValue(columnName, autoInflate = False)
                ref_cache_key = (column.reference(), ref_key)
                
                # cache this record so that we only access 1 of them
                if (not ref_cache_key in ref_cache):
                    col_value = record.recordValue(columnName, 
                                                   autoInflate = autoInflate)
                    ref_cache[ref_cache_key] = col_value
                else:
                    col_value = ref_cache[ref_cache_key]
            else:
                col_value = record.recordValue(columnName)
            
            column_data[columnName] = col_value
        
        if syntax:
            return projex.text.render(syntax, column_data)
        else:
            return column_data[columnName]
    
    @staticmethod
    def groupRecords(records, groupings, autoInflate=False):
        """
        Creates a grouping of the records based on the inputed columns.  You \
        can supply as many column values as you'd like creating nested \
        groups.
        
        :param      records     | <Table>
                    groupings     | [<str>, ..]
                    autoInflate | <bool>
        
        :return     <dict>
        """
        if autoInflate == None:
            autoInflate = True
            
        output      = {}
        ref_cache   = {}  # stores the grouping options for auto-inflated vars
        
        for record in records:
            data    = output
            schema  = record.schema()
            
            # make sure we have the proper level
            for i in range(len(groupings) - 1):
                grouping_key = Table.__groupingKey(record, 
                                                   schema, 
                                                   groupings[i], 
                                                   ref_cache, 
                                                   autoInflate)
                
                data.setdefault(grouping_key, {})
                data = data[grouping_key]
            
            grouping_key = Table.__groupingKey(record, 
                                               schema, 
                                               groupings[-1], 
                                               ref_cache, 
                                               autoInflate)
            
            data.setdefault(grouping_key, [])
            data[grouping_key].append(record)
        
        return output
    
    @classmethod
    def recordcheck(cls, obj):
        """
        Checks to see if the inputed obj ia s Table record instance.
        
        :param      obj     | <variant>
        
        :return     <bool>
        """
        return isinstance(obj, cls)
    
    @classmethod
    def typecheck(cls, obj):
        """
        Checks to see if the inputed obj is a subclass of a table.
        
        :param      obj     |  <variant>
                    cls     |  <subclass of Table> || None
        
        :return     <bool>
        """
        try:
            return issubclass(obj, cls)
        except TypeError:
            return False