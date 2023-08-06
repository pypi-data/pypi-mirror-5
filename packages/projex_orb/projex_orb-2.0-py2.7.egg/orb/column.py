#!/usr/bin/python

""" Defines the meta information for a column within a table schema. """

# define authorship information
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = ['Eric Hulser']
__copyright__       = 'Copyright (c) 2011, Projex Software'
__license__         = 'LGPL'

# maintanence information
__maintainer__      = 'Projex Software'
__email__           = 'team@projexsoftware.com'

#------------------------------------------------------------------------------

import datetime
import decimal
import logging
import re
from time import strptime

from xml.etree import ElementTree

import projex.text
import projex.regex
from projex import security
from projex.enum import enum

import orb
from orb.common import ColumnType, RemovedAction
from orb import errors

logger = logging.getLogger(__name__)

try:
    import pytz
except ImportError:
    pytz = None

class Column(object):
    """ Used to define database schema columns when defining Table classes. """
    
    # define default naming system
    TEMPLATE_PRIMARY_KEY = 'id'
    TEMPLATE_GETTER      = '[name::camelHump::lower_first]'
    TEMPLATE_SETTER      = 'set[name::camelHump::upper_first::lstrip(Is)]'
    TEMPLATE_FIELD       = '[name::underscore::lower]'
    TEMPLATE_DISPLAY     = '[name::upper_first::words]'
    TEMPLATE_INDEX       = 'by[name::camelHump::upper_first]'
    TEMPLATE_REVERSED    = '[name::reversed::camelHump::lower_first]'
    TEMPLATE_REFERENCE   = '[name::underscore::lower]_id'
    TEMPLATE_COMPLEX_REF = '[table::underscore::lower]_' \
                           '[name::underscore::lower]_id'
    
    TEMPLATE_MAP = {
        'getterName':   TEMPLATE_GETTER,
        'setterName':   TEMPLATE_SETTER,
        'fieldName':    TEMPLATE_FIELD,
        'displayName':  TEMPLATE_DISPLAY,
        'indexName':    TEMPLATE_INDEX,
        'primaryKey':   TEMPLATE_PRIMARY_KEY,
    }
    
    VALIDATOR_TYPES = {
        ColumnType.Email:       projex.regex.EMAIL,
        ColumnType.Password:    projex.regex.PASSWORD,
    }
    
    VALIDATOR_HELP = {
        ColumnType.Email:       projex.regex.EMAIL_HELP,
        ColumnType.Password:    projex.regex.PASSWORD_HELP
    }
    
    Flags = enum('ReadOnly',
                 'Proxy',
                 'Private',
                 'Referenced',
                 'Polymorphic',
                 'Primary',
                 'AutoIncrement',
                 'Required',
                 'Unique',
                 'Encrypted',
                 'Searchable')
    
    def __init__(self, typ, name, **options):
        # define required arguments
        self._name       = name
        self._type       = typ
        self._schema     = options.get('schema')
        self._engines    = {}
        self._customData = {}
        self._timezone   = None
        
        # set default values
        ref = options.get('reference', '')
        for key in Column.TEMPLATE_MAP.keys():
            if not key in options:
                options[key] = Column.defaultDatabaseName(key, name, ref)
        
        # naming & accessor options
        self._getter         = options.get('getter')
        self._getterName     = options.get('getterName')
        self._setter         = options.get('setter')
        self._setterName     = options.get('setterName')
        self._fieldName      = options.get('fieldName')
        self._displayName    = options.get('displayName')
        
        # format options
        self._stringFormat   = options.get('stringFormat', '')
        self._encoding       = options.get('encoding', 'utf-8')
        self._enum           = options.get('enum', None)
        
        # validation options
        self._validator     = None
        self._validatorText = options.get('validator',
                                          Column.VALIDATOR_TYPES.get(typ, ''))
        self._validatorHelp = options.get('validatorText',
                                          Column.VALIDATOR_HELP.get(typ, ''))
        
        # referencing options
        self._referenced    = options.get('referenced', False)
        self._reference     = options.get('reference', '')
        self._referenceRemovedAction = options.get('referenceRemovedAction',
                                                   RemovedAction.DoNothing)
        
        # reversed referencing options
        self._reversed       = options.get('reversed', False)
        self._reversedName   = options.get('reversedName', '')
        self._reversedCached = options.get('reversedCached', False)
        self._reversedCacheExpires = options.get('reversedCachedExpires', 0)
        
        # indexing options
        self._indexed       = options.get('indexed', False)
        self._indexCached   = options.get('indexCached', False)
        self._indexName     = options.get('indexName')
        self._indexCachedExpires = options.get('indexCachedExpires', 0)
        
        # additional properties
        self._default       = options.get('default', None)
        self._maxlength     = options.get('maxlength', 0)
        self._joiner        = options.get('joiner', None)
        self._aggregate     = options.get('aggregate', None)
        
        # flags options
        flags = 0
        if options.get('primary'):
            flags |= Column.Flags.Primary
        if options.get('proxy'):
            flags |= Column.Flags.Proxy
        if options.get('private'):
            flags |= Column.Flags.Private
        if options.get('readOnly'):
            flags |= Column.Flags.ReadOnly
        if options.get('polymorphic'):
            flags |= Column.Flags.Polymorphic
        if options.get('autoIncrement'):
            flags |= Column.Flags.AutoIncrement
        if options.get('required', options.get('primary')):
            flags |= Column.Flags.Required
        if options.get('unique'):
            flags |= Column.Flags.Unique
        if options.get('encrypted', typ == ColumnType.Password):
            flags |= Column.Flags.Encrypted
        if options.get('searchable'):
            flags |= Column.Flags.Searchable
        
        self._flags = options.get('flags', flags)
    
    def aggregate(self):
        """
        Returns the query aggregate that is associated with this column.
        
        :return     <orb.QueryAggregate>
        """
        if type(self._aggregate).__name__ == 'function':
            return self._aggregate(self)
        return self._aggregate
        
    def autoIncrement( self ):
        """
        Returns whether or not this column should 
        autoIncrement in the database.
        
        :sa         testFlag
        
        :return     <bool>
        """
        return self.testFlag(Column.Flags.AutoIncrement)
    
    def columnType(self, baseOnly=False):
        """
        Returns the type of data that this column represents.
        
        :return     <orb.common.ColumnType>
        """
        if baseOnly:
            return ColumnType.base(self._type)
        return self._type
    
    def columnTypeText(self, baseOnly=False):
        """
        Returns the column type text for this column.
        
        :return     <str>
        """
        return ColumnType[self.columnType(baseOnly=baseOnly)]
    
    def customData( self, key, default = None ):
        """
        Returns custom information that was assigned to this column for the \
        inputed key.  If no value was assigned to the given key, the inputed \
        default value will be returned.
        
        :param      key     | <str>
                    default | <variant>
            
        :return     <variant>
        """
        return self._customData.get(key, default)
    
    def engine(self, db=None):
        """
        Returns the data engine for this column for the given database.
        Individual databases can define their own data engines.  If no database
        is defined, then the currently active database will be used.
        
        :param      db | <orb.Database> || None
        
        :return     <orb.ColumnEngine> || None
        """
        try:
            return self._engines[db]
        except KeyError:
            engine = None
            
            # lookup the current database
            if db is None:
                db = orb.Orb.instance().database()
            
            # lookup the database engine for this instance
            if db:
                try:
                    engine = self._engines[db.databaseType()]
                except KeyError:
                    engine = db.columnEngine(self)
                
                self._engines[db] = engine
        
        return engine
    
    def default(self, resolve=False):
        """
        Returns the default value for this column to return
        when generating new instances.
        
        :return     <variant>
        """
        default = self._default
        ctype   = ColumnType.base(self.columnType())
        
        if not resolve:
            return default
        
        elif default == 'None':
            return None
        
        elif ctype == ColumnType.Bool:
            if type(default) == bool:
                return default
            else:
                return str(default) in ('True', '1')
        
        elif ctype in (ColumnType.Integer,
                       ColumnType.Enum,
                       ColumnType.BigInt,
                       ColumnType.Double):
            
            if type(default) in (str, unicode):
                try:
                    return eval(default)
                except SyntaxError:
                    return 0
            elif default is None:
                return 0
            else:
                return default
        
        elif ctype == ColumnType.Date:
            if isinstance(default, datetime.date):
                return default
            elif default in ('today', 'now'):
                return datetime.date.today()
            return None
            
        elif ctype == ColumnType.Time:
            if isinstance(default, datetime.time):
                return default
            elif default == 'now':
                return datetime.datetime.now().time()
            else:
                return None
            
        elif ctype == ColumnType.Datetime:
            if isinstance(default, datetime.datetime):
                return default
            elif default in ('today', 'now'):
                return datetime.datetime.now()
            else:
                return None
        
        elif ctype == ColumnType.DatetimeWithTimezone:
            if isinstance(default, datetime.datetime):
                return default
            elif default in ('today', 'now'):
                return datetime.datetime.utcnow()
            else:
                return None
        
        elif ctype == ColumnType.Interval:
            if isinstance(default, datetime.timedelta):
                return default
            elif default == 'now':
                return datetime.timedelta()
            else:
                return None
        
        elif ctype == ColumnType.Decimal:
            if default is None:
                return decimal.Decimal()
            return default
        
        elif ctype & (ColumnType.String | \
                      ColumnType.Text | \
                      ColumnType.Url | \
                      ColumnType.Email | \
                      ColumnType.Password | \
                      ColumnType.Filepath | \
                      ColumnType.Directory | \
                      ColumnType.Xml | \
                      ColumnType.Html | \
                      ColumnType.Color):
            if default is None:
                return ''
            return default
        
        else:
            return None
    
    def defaultOrder(self):
        """
        Returns the default ordering for this column based on its type.
        
        Strings will be desc first, all other columns will be asc.
        
        
        :return     <str>
        """
        if self.isString():
            return 'desc'
        return 'asc'
    
    def displayName(self, autoGenerate=True):
        """
        Returns the display name for this column - if no name is \
        explicitly set, then the words for the column name will be \
        used.
        
        :param      autoGenerate | <bool>
        
        :return     <str>
        """
        if ( not autoGenerate or self._displayName ):
            return self._displayName
        
        return projex.text.capitalizeWords( self.name() )
    
    def encoding(self):
        """
        Returns the encoding that is used for this column in the database.
        
        :return     <str>
        """
        return self._encoding
    
    def enum(self):
        """
        Returns the enumeration that is associated with this column.  This can
        help for automated validation when dealing with enumeration types.
        
        :return     <projex.enum.enum> || None
        """
        return self._enum
    
    def getter(self):
        """
        Returns the getter method linked with this column.  This is used in
        proxy columns.
        
        :return     <callable> || None
        """
        return self._getter
    
    def fieldName( self ):
        """
        Returns the field name that this column will have inside
        the database.  The Column.TEMPLATE_FIELD variable will be
        used for this property by default.
                    
        :return     <str>
        """
        return self._fieldName
    
    def firstMemberSchema(self, schemas):
        """
        Returns the first schema within the list that this column is a member
        of.
        
        :param      schemas | [<orb.TableSchema>, ..]
        
        :return     <orb.TableSchema> || None
        """
        for schema in schemas:
            if schema.hasColumn(self):
                return schema
        return self.schema()
    
    def flags(self):
        """
        Returns the flags that have been set for this column.
        
        :return     <Column.Flags>
        """
        return self._flags
    
    def getterName( self ):
        """
        Returns the name for the getter method that will be 
        generated for this column.  The Column.TEMPLATE_GETTER 
        variable will be used for this property by default.
        
        :return     <str>
        """
        return self._getterName
    
    def indexed( self ):
        """
        Returns whether or not this column is indexed for quick
        lookup.
        
        :return     <bool>
        """
        return self._indexed
    
    def indexCached(self):
        """
        Returns whether or not the index for this column should cache the
        records.
        
        :return     <bool>
        """
        return self._indexCached
    
    def indexCachedExpires(self):
        """
        Returns the time in seconds for how long to store a client side cache
        of the results for the index on this column.
        
        :return     <int>
        """
        return self._indexCachedExpires
    
    def indexName( self ):
        """
        Returns the name to be used when generating an index
        for this column.
        
        :return     <str>
        """
        return self._indexName
    
    def isAggregate(self):
        """
        Returns whether or not this column is a aggregate.
        
        :return     <bool>
        """
        return self._aggregate is not None
    
    def isEncrypted( self ):
        """
        Returns whether or not the data in this column should be encrypted.
        
        :return     <bool>
        """
        return self.testFlag(Column.Flags.Encrypted)
    
    def isJoined(self):
        """
        Returns whether or not this column is a joined column.  Dynamic
        columns are not actually a part of the database table, but rather
        joined in data using a query during selection.
        
        :return     <bool>
        """
        return self._joiner is not None
    
    def isMatch(self, name):
        """
        Returns whether or not this column's text info matches the inputed name.
        
        :param      name | <str>
        """
        opts = (self.name(),
                self.name().strip('_'),
                self.fieldName(),
                self.displayName())
        
        return name in opts
    
    def isMemberOf(self, schemas):
        """
        Returns whether or not this column is a member of any of the given
        schemas.
        
        :param      schemas | [<orb.TableSchema>, ..] || <orb.TableSchema>
        
        :return     <bool>
        """
        if type(schemas) not in (tuple, list, set):
            schemas = (schemas,)
        
        for schema in schemas:
            if schema.hasColumn(self):
                return True
        return False
    
    def isPolymorphic(self):
        """
        Returns whether or not this column defines the polymorphic class
        for the schema.  If this is set to True in conjunction with a
        reference model, the text for the reference model will be used
        to try to inflate the record to its proper class.
        
        :sa         testFlag
        
        :return     <bool>
        """
        return self.testFlag(Column.Flags.Polymorphic)
    
    def isPrivate(self):
        """
        Returns whether or not this column should be treated as private.
        
        :sa         testFlag
        
        :return     <bool>
        """
        return self.testFlag(Column.Flags.Private)
    
    def isProxy(self):
        """
        Retursn whether or not this column is a proxy column.
        
        :sa         testFlag
        
        :return     <bool>
        """
        return self.testFlag(Column.Flags.Proxy)
    
    def isReadOnly(self):
        """
        Returns whether or not this column is read-only.
        
        :sa         testFlag
        
        :return     <bool>
        """
        return self.testFlag(Column.Flags.ReadOnly)
    
    def isReference( self ):
        """
        Returns whether or not this column is a reference to another table.
        
        :return     <bool>
        """
        if self._reference:
            return True
        return False
    
    def isReferenced(self):
        """
        Returns whether or not this column is referenced from an external file.
        
        :return     <bool>
        """
        return self._referenced
    
    def isReversed(self):
        """
        Returns whether or not this column generates a reverse lookup method \
        for its reference model.
        
        :return     <bool>
        """
        return self._reversed   
    
    def isSearchable(self):
        """
        Returns whether or not this column is a searchable column.  If it is,
        when the user utilizes the search function for a record set, this column
        will be used as a matchable entry.
        
        :sa         testFlag
        
        :return     <bool>
        """
        return self.testFlag(Column.Flags.Searchable)
    
    def isString(self):
        """
        Returns whether or not this column is of a string type.
        
        :return     <bool>
        """
        string_types  = ColumnType.String
        string_types |= ColumnType.Text
        string_types |= ColumnType.Url
        string_types |= ColumnType.Email
        string_types |= ColumnType.Password
        string_types |= ColumnType.Filepath
        string_types |= ColumnType.Directory
        string_types |= ColumnType.Xml
        string_types |= ColumnType.Html
        string_types |= ColumnType.Color
        
        return (ColumnType.base(self.columnType()) & string_types) != 0
    
    def iterFlags(self):
        """
        Returns the flags that are currently set for this instance.
        
        :return     [<Column.Flags>, ..]
        """
        return [flag for flag in Column.Flags.values() if self.testFlag(flag)]
    
    def joiner(self):
        """
        Returns the joiner query that is used to define what this columns
        value will be.
        
        :return     (<orb.Column>, <orb.Query>) || None
        """
        joiner = self._joiner
        if type(joiner).__name__ == 'function':
            return joiner(self)
        return joiner
    
    def maxlength(self):
        """
        Returns the max length for this column.  This property
        is used for the varchar data type.
        
        :return     <int>
        """
        return self._maxlength
    
    def memberOf(self, schemas):
        """
        Returns a list of schemas this column is a member of from the inputed
        list.
        
        :param      schemas | [<orb.TableSchema>, ..]
        
        :return     [<orb.TableSchema>, ..]
        """
        for schema in schemas:
            if schema.hasColumn(self):
                yield schema
    
    def name(self):
        """
        Returns the accessor name that will be used when 
        referencing this column around the app.
        
        :return     <str>
        """
        return self._name
    
    def primary(self):
        """
        Returns if this column is one of the primary keys for the
        schema.
        
        :sa         testFlag
        
        :return     <bool>
        """
        return self.testFlag(Column.Flags.Primary)
    
    def reference(self):
        """
        Returns the model that this column is related to when
        it is a foreign key.
                    
        :return     <str>
        """
        return self._reference
    
    def referenceRemovedAction(self):
        """
        Determines how records for this column will act when the reference it
        points to is removed.
        
        :return     <ReferencedAction>
        """
        return self._referenceRemovedAction
    
    def referenceModel(self):
        """
        Returns the model that this column references.
        
        :return     <Table> || None
        """
        if not self.isReference():
            return None
        
        dbname = self.schema().databaseName()
        return orb.Orb.instance().model(self.reference(), database=dbname)
    
    def restoreValue(self, value):
        """
        Restores the value from a table cache for usage.
        
        :param      value | <variant>
        """
        coltype = ColumnType.base(self.columnType())
        
        # restore a datetime timezone value
        if isinstance(value, datetime.datetime) and \
           coltype == ColumnType.DatetimeWithTimezone:
            tz = self.timezone()
            
            if tz is not None:
                if value.tzinfo is None:
                    value = tz.fromutc(value)
                else:
                    value = value.astimezone(tz)
            else:
                logger.warning('No local timezone has been defined')
        
        # ensure we have a properly encoded value
        elif type(value) == str and \
             self.encoding() and self.encoding() != 'ascii':
            return projex.text.encoded(value, self.encoding())
        
        return value
    
    def required(self):
        """
        Returns whether or not this column is required when
        creating records in the database.
        
        :sa         testFlag
        
        :return     <bool>
        """
        return self.testFlag(Column.Flags.Required)
    
    def reversedCached(self):
        """
        Returns whether or not the reverse lookup for this column should
        be cached.
        
        :return     <bool>
        """
        return self._reversedCached
    
    def reversedCacheExpires(self):
        """
        Returns the time in seconds that the cache should expire within.  If
        the value is 0, then the cache will never expire
        
        :return     <int>
        """
        return self._reversedCacheExpires
    
    def reversedName(self):
        """
        Returns the name that will be used when generating a reverse accessor \
        for its reference table.
        
        :return     <str>
        """
        return self._reversedName
    
    def storeValue(self, value):
        """
        Converts the value to one that is safe to store on a record within
        the record values dictionary
        
        :param      value | <variant>
        
        :return     <variant>
        """
        coltype = ColumnType.base(self.columnType())
        
        if value is None:
            return value
        
        # store timezone information
        elif coltype == ColumnType.DatetimeWithTimezone and \
             isinstance(value, datetime.datetime):
            
            tz = self.timezone()
            if tz is not None:
                # ensure we have some timezone information before converting
                # to UTC time
                if value.tzinfo is None:
                    value = tz.localize(value, is_dst=None)
                
                value = value.astimezone(pytz.utc).replace(tzinfo=None)
            else:
                logger.warning('No local timezone defined.')
        
        # convert standard string values to ascii for the database
        elif coltype == ColumnType.String:
            return projex.text.toAscii(value)
        
        # convert other types of string values to the encoded value
        elif self.isString():
            return projex.text.encoded(value, self.encoding())
        
        # encrypt the value if necessary
        elif self.isEncrypted():
            return security.encrypt(value)
        
        return value
    
    def schema(self):
        """
        Returns the table that this column is linked to in the database.
        
        :return     <TableSchema>
        """
        return self._schema
    
    def setterName(self):
        """
        Returns the setter name that will be used to generate the
        setter method on the table as it is generated.  The
        Column.TEMPLATE_SETTER property will be used by default.
        
        :return     <str>
        """
        return self._setterName
    
    def setter(self):
        """
        Returns the setter method linked with this column.  This is used in
        proxy columns.
        
        :return     <callable> || None
        """
        return self._setter
    
    def setAutoIncrement(self, state):
        """
        Sets whether or not this column should auto increment.
        
        :sa         setFlag
        
        :param      state | <bool>
        """
        self.setFlag(Column.Flags.AutoIncrement, state)
    
    def setColumnType(self, columnType):
        """
        Sets the column type that this column represents in the database.
        
        :param      columnType | <ColumnType>
        """
        self._type = columnType
    
    def setCustomData(self, key, value):
        """
        Sets the custom data at the inputed key to the given value.
        
        :param      key     | <str>
                    value   | <variant>
        """
        self._customData[str(key)] = value
    
    def setJoiner(self, joiner):
        """
        Sets the joiner query for this column to the inputed query.
        
        :param      query | (<orb.Column>, <orb.Query>) || <callable> || None
        """
        self._joiner = joiner
        if joiner is not None:
            self.setFlag(Column.Flags.ReadOnly)
    
    def setEngine(self, db_or_type, engine):
        """
        Sets the database engine for this column in the given database.
        
        :param      db_or_type | <orb.Database> || <str>
                    engine     | <orb.ColumnEngine>
        """
        self._engines[db_or_type] = engine
    
    def setDefault(self, default):
        """
        Sets the default value for this column to the inputed value.
        
        :param      default | <str>
        """
        self._default = default
    
    def setDisplayName(self, displayName):
        """
        Sets the display name for this column.
        
        :param      displayName | <str>
        """
        if ( displayName is not None ):
            self._displayName = displayName
    
    def setEnum(self, enum):
        """
        Sets the enumeration that is associated with this column to the inputed
        type.  This is an optional parameter but can be useful when dealing
        with validation and some of the automated features of the ORB system.
        
        :param      enum | <projex.enum.enum> || None
        """
        self._enum = enum
    
    def setEncoding(self, encoding):
        """
        Sets the encoding that will be used for this column in the database.
        
        :param      encoding | <str>
        """
        self._encoding = encoding
    
    def setEncrypted(self, state):
        """
        Sets whether or not this column is encrypted in the database.
        
        :sa         setFlag
        
        :param      state   | <bool>
        """
        self.setFlag(Column.Flags.Encrypted, state)
    
    def setFieldName(self, fieldName):
        """
        Sets the field name for this column.
        
        :param      fieldName | <str>
        """
        if fieldName is not None:
            self._fieldName = fieldName
    
    def setFlag(self, flag, state=True):
        """
        Sets whether or not this flag should be on.
        
        :param      flag  | <Column.Flags>
                    state | <bool>
        """
        has_flag = self.testFlag(flag)
        if has_flag and not state:
            self.setFlags(self.flags() ^ flag)
        elif not has_flag and state:
            self.setFlags(self.flags() | flag)
    
    def setFlags(self, flags):
        """
        Sets the global flags for this column to the inputed flags.
        
        :param      flags | <Column.Flags>
        """
        self._flags = flags
    
    def setName(self, name):
        """
        Sets the name of this column to the inputed name.
        
        :param      name    | <str>
        """
        self._name = name
    
    def setGetterName(self, getterName):
        """
        Sets the getter name for this column.
        
        :param      getterName | <str>
        """
        if ( getterName is not None ):
            self._getterName = getterName
    
    def setIndexed(self, state):
        """
        Sets whether or not this column will create a lookup index.
        
        :param      state   | <bool>
        """
        self._indexed = state
    
    def setIndexCached(self, cached):
        """
        Sets whether or not the index should cache the results from the
        database when looking up this column.
        
        :param      cached | <bool>
        """
        self._indexCached = cached
    
    def setIndexCachedExpires(self, seconds):
        """
        Sets the time in seconds for how long to store a client side cache
        of the results for the index on this column.
        
        :param     seconds | <int>
        """
        self._indexCachedExpires = seconds
    
    def setIndexName(self, indexName):
        """
        Sets the index name for this column.
        
        :param      indexName | <str>
        """
        if ( indexName is not None ):
            self._indexName = indexName
    
    def setMaxlength(self, length):
        """
        Sets the maximum length for this column.  Used when defining string \
        column types.
        
        :param      length | <int>
        """
        self._maxlength = length
    
    def setPolymorphic(self, state):
        """
        Sets whether or not this column defines a polymorphic mapper for
        the table.
        
        :sa         setFlag
        
        :param      state | <bool>
        """
        self.setFlag(Column.Flags.Polymorphic, state)
    
    def setPrimary(self, primary):
        """
        Sets whether or not this column is one of the primary columns \
        for a table.
        
        :sa         setFlag
        
        :param      primary     | <bool>
        """
        self.setFlag(Column.Flags.Primary, primary)
    
    def setPrivate(self, state):
        """
        Sets whether or not this column should be treated as a private column.
        
        :sa         setFlag
        
        :param      state | <bool>
        """
        self.setFlag(Column.Flags.Private, state)
    
    def setAggregate(self, aggregate):
        """
        Sets the query aggregate for this column to the inputed aggregate.
        
        :param      aggregate | <orb.QueryAggregate> || None
        """
        self._aggregate = aggregate
        if aggregate is not None:
            self.setFlag(Column.Flags.ReadOnly)
    
    def setReadOnly(self, state):
        """
        Sets whether or not this column is a read only attribute.
        
        :sa         setFlag
        
        :param      state | <bool>
        """
        self.setFlag(Column.Flags.ReadOnly, state)
    
    def setReference(self, reference):
        """
        Sets the name of the table schema instance that this column refers \
        to from its schema.
        
        :param      reference       | <str>
        """
        self._reference = reference
    
    def setReferenceRemovedAction(self, referencedAction):
        """
        Sets how records for this column will act when the reference it
        points to is removed.
        
        :param     referencedAction | <ReferencedAction>
        """
        self._referenceRemovedAction = referencedAction
    
    def setRequired(self, required):
        """
        Sets whether or not this column is required in the databse.
        
        :sa         setFlag
        
        :param      required | <bool>
        """
        self.setFlag(Column.Flags.Required, required)
    
    def setReversed(self, state):
        """
        Sets whether or not this column generates a reverse accessor for \
        lookups to its reference table.
        
        :param      state | <bool>
        """
        self._reversed = state
    
    def setReversedCached(self, state):
        """
        Sets whether or not the reverse lookup for this column should be
        cached.
        
        :param      state | <bool>
        """
        self._reversedCached = state
    
    def setReversedCacheExpires(self, seconds):
        """
        Sets the time in seconds that the cache will remain on the client side
        before needing to request an update from the server.  If the seconds
        is 0, then the cache will never expire.
        
        :param      seconds | <int>
        """
        self._reversedCacheExpires = seconds
    
    def setReversedName(self, reversedName):
        """
        Sets the reversing name for the method that will be generated for the \
        lookup to its reference table.
        
        :param      reversedName | <str>
        """
        if reversedName is not None:
            self._reversedName = reversedName
    
    def setSearchable(self, state):
        """
        Sets whether or not this column is used during record set searches.
        
        :sa         setFlag
        
        :param      state | <bool>
        """
        self.setFlag(Column.Flags.Searchable, state)
    
    def setSetterName(self, setterName):
        """
        Sets the setter name for this column.
        
        :param      setterName | <str>
        """
        if setterName is not None:
            self._setterName = setterName
    
    def setStringFormat(self, formatter):
        """
        Sets the string formatter for this column to the inputed text.  This
        will use Python's string formatting system to format values for the
        column when it is displaying its value.
        
        :param      formmater | <str>
        """
        self._stringFormat = formatter
    
    def setTimezone(self, timezone):
        """
        Sets the timezone associated directly to this column.
        
        :sa     <orb.Orb.setTimezone>
        
        :param     timezone | <pytz.tzfile> || None
        """
        self._timezone = timezone
    
    def setUnique(self, state):
        """
        Sets whether or not this column is unique in the database.
        
        :param      setFlag
        
        :param      unique | <bool>
        """
        self.setFlag(Column.Flags.Unique, state)
    
    def setValidatorText(self, text):
        """
        Sets the validation pattern for this column.
        
        :param      text | <str>
        """
        self._validatorText = text
        self._validator = None
    
    def setValidatorHelp(self, text):
        """
        Sets the validation help for this column.
        
        :param      text | <str>
        """
        self._validatorHelp = text
    
    def stringFormat(self):
        """
        Returns the string formatter for this column to the inputed text.  This
        will use Python's string formatting system to format values for the
        column when it is displaying its value.
        
        :return     <str>
        """
        return self._stringFormat
    
    def testFlag(self, flag):
        """
        Tests to see if this column has the inputed flag set.
        
        :param      flag | <Column.Flags>
        """
        return (self.flags() & flag) != 0
    
    def timezone(self):
        """
        Returns the timezone associated specifically with this column.  If
        no timezone is directly associated, then it will return the timezone
        that is associated with the Orb system in general.
        
        :sa     <orb.Orb>
        
        :return     <pytz.tzfile> || None
        """
        if self._timezone is None:
            return self.schema().timezone()
        return self._timezone
    
    def toXml(self, xparent):
        """
        Saves the data about this column out to xml as a child node for the
        inputed parent.
        
        :param      xparent    | <xml.etree.ElementTree.Element>
        
        :return     <xml.etree.ElementTree.Element>
        """
        xcolumn = ElementTree.SubElement( xparent, 'column' )
        
        # save the properties
        xcolumn.set('type', ColumnType[self.columnType()])
        xcolumn.set('name', self.name())
        xcolumn.set('display', self.displayName(False))
        xcolumn.set('getter', self.getterName())
        xcolumn.set('setter', self.setterName())
        xcolumn.set('field', self.fieldName())
        
        # store indexing options
        xcolumn.set('index', self.indexName())
        xcolumn.set('indexed', str(self.indexed()))
        xcolumn.set('indexCached', str(self.indexCached()))
        xcolumn.set('indexCachedExpires', str(self.indexCachedExpires()))
        
        if self.default() is not None:
            xcolumn.set('default', str(self.default()))
        
        # store additional options
        xcolumn.set('maxlen', str(self.maxlength()))
        
        # store flags
        for flag in Column.Flags.keys():
            key = flag[0].lower() + flag[1:]
            xcolumn.set(key, str(self.testFlag(Column.Flags[flag])))
        
        # store validation options
        vtext = self.validatorText()
        vhelp = self.validatorHelp()
        if vtext:
            xcolumn.set('validatorText', vtext)
        if vhelp:
            xcolumn.set('validatorHelp', vhelp)
        
        # store referencing options
        if self.reference():
            xrelation = ElementTree.SubElement( xcolumn, 'relation' )
            xrelation.set('table', self.reference())
            xrelation.set('reversed', str(self.isReversed()))
            xrelation.set('reversedName', self.reversedName())
            xrelation.set('removedAction', str(self.referenceRemovedAction()))
            xrelation.set('cached', str(self.reversedCached()))
            xrelation.set('expires', str(self.reversedCacheExpires()))
        
        # store string format options
        if self._stringFormat:
            xformat = ElementTree.SubElement(xcolumn, 'format')
            xformat.text = self._stringFormat
        
        return xcolumn
        
    def unique(self):
        """
        Returns whether or not this column should be unique in the
        database.
                    
        :return     <bool>
        """
        return self.testFlag(Column.Flags.Unique)
    
    def validate(self, value):
        """
        Validates the inputed value against this columns rules.
        
        :param      value | <variant>
        
        :return     (<bool> success, <str> message)
        """
        # don't validate against the primary field
        if self.primary():
            return (True, '')
        
        # validate against expression information
        validator = self.validator()
        if validator:
            if not value in (str, unicode):
                try:
                    value = str(value)
                except:
                    return (False, str(errors.ValidationError(self, value)))
            
            if not validator.match(value):
                if not self.isEncrypted() and len(value) < 40:
                    return (False,  str(errors.ValidationError(self, value)))
            
        # validate against requirement parameters
        if self.required() and value in ('', None):
            return (False, '%s is a required value.' % self.displayName())
        
        return (True, '')
    
    def validator(self):
        """
        Returns the regular expression pattern validator for this column.
        
        :return     <SRE_Pattern> || None
        """
        if not self._validator and self._validatorText:
            try:
                self._validator = re.compile(self._validatorText)
            except:
                schema = self.schema()
                if schema:
                    err = schema.name() + '.' + self.name()
                else:
                    err = self.name()
                
                err += ': "%s" is not a valid regular expression'
                err %= self._validatorText
                
                logger.error(err)
        
        return self._validator
    
    def validatorText(self):
        """
        Returns the validation text that is used to generate the validator \
        for this column.
        
        :return     <str>
        """
        return self._validatorText
    
    def validatorHelp(self):
        """
        Returns the help string associated with this columns validation \
        checker.
        
        :return     <str>
        """
        return self._validatorHelp
    
    def valueFromString(self, value, extra=None, db=None):
        """
        Converts the inputed string text to a value that matches the type from
        this column type.
        
        :param      value | <str>
                    extra | <variant>
        """
        # convert the value from a string value via the data engine system
        engine = self.engine(db)
        if engine:
            return engine.fromString(value)
        
        # convert the value to a string using default values
        coltype = ColumnType.base(self.columnType())
        if coltype == ColumnType.Date:
            if extra == None:
                extra = '%Y-%m-%d'
            
            time_struct = strptime(value, extra)
            return datetime.date(time_struct.tm_year,
                                 time_struct.tm_month,
                                 time_struct.tm_day)
        
        elif coltype == ColumnType.Time:
            if extra == None:
                extra = '%h:%m:%s'
            
            time_struct = strptime(value, extra)
            return datetime.time(time_struct.tm_hour,
                                 time_struct.tm_min,
                                 time_struct.tm_sec)
        
        elif coltype == ColumnType.Datetime:
            if extra == None:
                extra = '%Y-%m-%d %h:%m:s'
            
            time_struct = strptime(value, extra)
            return datetime.datetime(time_struct.tm_year,
                                     time_struct.tm_month,
                                     time_struct.tm_day,
                                     time_struct.tm_hour,
                                     time_struct.tm_minute,
                                     time_struct.tm_sec)
        
        elif coltype == ColumnType.Bool:
            return str(value).lower() == 'true'
        
        elif coltype in (ColumnType.Integer, 
                         ColumnType.Double,
                         ColumnType.Decimal,
                         ColumnType.BigInt,
                         ColumnType.Enum):
            try:
                value = eval(value)
            except ValueError:
                value = 0
            
            return value
        
        return str(value)
    
    def valueToString(self, value, extra=None, db=None):
        """
        Converts the inputed string text to a value that matches the type from
        this column type.
        
        :sa         engine
        
        :param      value | <str>
                    extra | <variant>
        """
        # convert the value to a string value via the data engine system
        engine = self.engine(db)
        if engine:
            return engine.toString(value)
        
        # convert the value to a string using default values
        coltype = ColumnType.base(self.columnType())
        
        if coltype == ColumnType.Date:
            if extra == None:
                extra = '%Y-%m-%d'
            
            return value.strftime(extra)
            
        elif coltype == ColumnType.Time:
            if extra == None:
                extra = '%h:%m:%s'
            
            return value.strftime(extra)
            
        elif coltype == ColumnType.Datetime:
            if extra == None:
                extra = '%Y-%m-%d %h:%m:s'
            
            return value.strftime(extra)
        
        return str(value)
    
    @staticmethod
    def defaultDatabaseName(typ, name, reference=''):
        """
        Returns the default schema name based on the current column templates.
        
        :param      typ         |  <str>
                    name        |  <str>
                    reference   | <str> | table the column refers to
        
        :return     <str>
        """
        # make sure we have an actual name to process
        name = str(name).strip()
        if not name:
            return ''
        
        # generate a reference field type
        if typ == 'fieldName' and reference:
            if name.lower() == reference.lower():
                templ = Column.TEMPLATE_REFERENCE
            else:
                templ = Column.TEMPLATE_COMPLEX_REF
        
        # generate the default templates
        else:
            templ = Column.TEMPLATE_MAP.get(typ)
            
        if templ == None:
            return ''
        
        return projex.text.render(templ,  {'name':  name,  'table': reference})
    
    @staticmethod
    def defaultPrimaryColumn(name):
        """
        Creates a default primary column based on the inputed table schema.
        
        :return     <Column>
        """
        
        # generate the auto column
        fieldName   = Column.defaultDatabaseName( 'primaryKey', name)
        column      = Column(ColumnType.Integer, 'id')
        column.setPrimary(True)
        column.setFieldName(fieldName)
        column.setAutoIncrement(True)
        column.setRequired(True)
        column.setUnique(True)
        
        return column
        
    @staticmethod
    def fromXml(xcolumn, referenced=False):
        """
        Generates a new column from the inputed xml column data.
        
        :param      xcolumn | <xml.etree.Element>
        
        :return     <Column> || None
        """
        typ  = ColumnType.get( xcolumn.get('type') )
        name = xcolumn.get('name')
        if typ is None or not name:
            return None
        
        # create the column
        column = Column(typ, name, referenced=referenced)
        
        column.setGetterName(xcolumn.get('getter'))
        column.setSetterName(xcolumn.get('setter'))
        column.setFieldName(xcolumn.get('field'))
        column.setDisplayName(xcolumn.get('display'))
        
        # restore indexing options
        column.setIndexName(xcolumn.get('index'))
        column.setIndexed(xcolumn.get('indexed') == 'True')
        column.setIndexCached(xcolumn.get('indexCached') == 'True')
        column.setIndexCachedExpires(int(xcolumn.get('indexCachedExpires',
                                                  column.indexCachedExpires())))
        
        column.setDefault(xcolumn.get('default', None))
        
        maxlen = xcolumn.get('maxlen')
        if maxlen is not None:
            column.setMaxlength(int(maxlen))
        
        # restore flags
        flags = 0
        for flag in Column.Flags.keys():
            state = xcolumn.get(flag[0].lower() + flag[1:]) == 'True'
            if state:
                flags |= Column.Flags[flag]
        
        column.setFlags(flags)
        
        # restore validation options
        vtext = xcolumn.get('validatorText')
        vhelp = xcolumn.get('validatorHelp')
        if vtext and vtext != 'None':
            column.setValidatorText(vtext)
        if vhelp and vhelp != 'None':
            column.setValidatorHelp(vhelp)
        
        # create relation information
        xrelation = xcolumn.find('relation')
        if xrelation is not None:
            column.setReference(xrelation.get('table', '') )
            column.setReversed(xrelation.get('reversed') == 'True')
            column.setReversedName(xrelation.get('reversedName'))
            column.setReversedCached(xrelation.get('cached') == 'True')
            
            exp = column.reversedCacheExpires()
            column.setReversedCacheExpires(int(xrelation.get('expires', exp)))
            
            action = int(xrelation.get('removedAction', 1))
            column.setReferenceRemovedAction( action )
        
        # restore formatting options
        xformat = xcolumn.find('format')
        if xformat is not None:
            column._stringFormat = xformat.text
        
        return column