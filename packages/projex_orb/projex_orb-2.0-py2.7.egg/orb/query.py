#!/usr/bin/python

"""
Defines the global query building syntzx for generating db
agnostic queries quickly and easily.
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
import os
import re
import projex.text
import logging

from xml.etree import ElementTree
from xml.parsers.expat import ExpatError

import orb
from orb.common import ColumnType, SearchMode
from orb import errors

from projex.enum import enum

logger = logging.getLogger(__name__)

FIELD_SYNTAX = os.environ.get('ORB_FIELD_SYNTAX', '(?P<%s>[\w_\.]+)')
VALUE_SYNTAX = os.environ.get('ORB_VALUE_SYNTAX', 
                              '(?P<%s>([\w\-_\.,]+|"[^"]+")|\[[^\]]+\])')

class QueryPattern(object):
    def __init__(self, syntax):
        self._syntax = syntax
        
        field       = FIELD_SYNTAX % 'field'
        value       = VALUE_SYNTAX % 'value'
        val_min     = VALUE_SYNTAX % 'min'
        val_max     = VALUE_SYNTAX % 'max'
        
        opts = {'value': value, 
                'min': val_min, 
                'max': val_max,
                'field': field}
        
        expr = syntax % opts
        
        self._pattern = re.compile(expr)
    
    def pattern(self):
        """
        Returns the regular expression pattern for this pattern.
        
        :return     <re.SRE_Pattern>
        """
        return self._pattern
    
    def syntax(self):
        """
        Returns the string syntax to be used for this pattern.
        
        :return     <str>
        """
        return self._syntax

#----------------------------------------------------------------------

class QueryAggregate(object):
    def __init__(self, typ, table, **options):
        self._type = typ
        self._table = table
        self._lookupOptions = orb.LookupOptions(**options)
    
    def lookupOptions(self):
        """
        Returns the lookup options instance for this aggregate.
        
        :return     <orb.LookupOptions>
        """
        return self._lookupOptions
    
    def table(self):
        """
        Returns the table associated with this aggregate.
        
        :return     <orb.Table>
        """
        return self._table
    
    def type(self):
        """
        Returns the type for this aggregate.
        
        :return     <str>
        """
        return self._type
    
    
#------------------------------------------------------------------------------

class Query(object):
    """ 
    Defines the central class for the abstract query markup language.
    
    For more information, refer to the [[$ROOT/querying|querying documentation]]
    
    """
    
    Op = enum(
        # equality operators
        'Is',
        'IsNot',
        
        # comparison operators
        'LessThan',
        'LessThanOrEqual',
        'Before',
        'GreaterThan',
        'GreaterThanOrEqual',
        'After',
        'Between',
        
        # string operators
        'Contains',
        'DoesNotContain',
        'Startswith',
        'Endswith',
        'Matches',
        'DoesNotMatch',
        
        # list operators
        'IsIn',
        'IsNotIn'
    )
    
    OffsetType = enum(
        'Add',
        'Subtract',
        'Multiply',
        'Divide',
        'And',
        'Or'
    )
    
    Function = enum(
        'Lower',
        'Upper',
        'Abs'
    )
    
    OffsetSymbol = {
        OffsetType.Add: '+',
        OffsetType.Subtract: '-',
        OffsetType.Multiply: '*',
        OffsetType.Divide: '/',
        OffsetType.And: '&',
        OffsetType.Or: '|'
    }
    
    SyntaxPatterns = [
        (Op.IsNotIn,            QueryPattern('%(field)s is not in %(value)s')),
        (Op.IsIn,               QueryPattern('%(field)s is in %(value)s')),
        (Op.IsNot,              QueryPattern('%(field)s is not %(value)s')),
        (Op.Is,                 QueryPattern('%(field)s is %(value)s')),
        (Op.LessThanOrEqual,    QueryPattern('%(field)s <= %(value)s')),
        (Op.LessThan,           QueryPattern('%(field)s < %(value)s')),
        (Op.Before,             QueryPattern('%(field)s before %(value)s')),
        (Op.GreaterThanOrEqual, QueryPattern('%(field)s >= %(value)s')),
        (Op.GreaterThan,        QueryPattern('%(field)s > %(value)s')),
        (Op.After,              QueryPattern('%(field)s after %(value)s')),
        (Op.Between,            QueryPattern('%(field)s between %(value)s')),
        (Op.Contains,           QueryPattern('%(field)s contains %(value)s')),
        (Op.DoesNotContain,     QueryPattern('%(field)s doesnt contain %(value)s')),
        (Op.Startswith,         QueryPattern('%(field)s startwith %(value)s')),
        (Op.Endswith,           QueryPattern('%(field)s endswith %(value)s')),
        (Op.Matches,            QueryPattern('%(field)s matches %(value)s')),
        (Op.DoesNotMatch,       QueryPattern('%(field)s doesnt match %(value)s')),
    ]
    
    ColumnOps = {
        # default option
        None: (
            Op.Is,
            Op.IsNot,
            Op.Contains,
            Op.DoesNotContain,
            Op.Startswith,
            Op.Endswith,
            Op.Matches,
            Op.DoesNotMatch,
            Op.IsNotIn,
            Op.IsIn
        ),
        # column specific options
        ColumnType.Bool: (
            Op.Is,
            Op.IsNot
        ),
        ColumnType.ForeignKey: (
            Op.Is,
            Op.IsNot,
            Op.IsIn,
            Op.IsNotIn
        ),
        ColumnType.Date: (
            Op.Is,
            Op.IsNot,
            Op.Before,
            Op.After,
            Op.Between,
            Op.IsIn,
            Op.IsNotIn
        ),
        ColumnType.Datetime: (
            Op.Is,
            Op.IsNot,
            Op.Before,
            Op.After,
            Op.Between,
            Op.IsIn,
            Op.IsNotIn
        ),
        ColumnType.Time: (
            Op.Is,
            Op.IsNot,
            Op.Before,
            Op.After,
            Op.Between,
            Op.IsIn,
            Op.IsNotIn
        )
    }
    
    # additional option values to control query flow
    UNDEFINED   = '__QUERY__UNDEFINED__'
    NOT_EMPTY   = '__QUERY__NOT_EMPTY__'
    EMPTY       = '__QUERY__EMPTY__'
    ALL         = '__QUERY__ALL__'

    def __str__( self ):
        return self.toString()
    
    def __nonzero__( self ):
        return not self.isNull()
    
    def __contains__( self, value ):
        """
        Returns whether or not the query defines the inputed column name.
        
        :param      value | <variant>
        
        :return     <bool>
        
        :usage      |>>> from orb import Query as Q
                    |>>> q = Q('testing') == True
                    |>>> 'testing' in q
                    |True
                    |>>> 'name' in q
                    |False
        """
        return value == self._columnName
        
    def __init__(self, *args, **options):
        """
        Initializes the Query instance.  The only required variable
        is the column name, the rest can be manipulated after
        creation.  This class takes a variable set of information
        to initialize.  You can initialize a blank query object
        by supplying no arguments, which is useful when generating
        queries in a loop, or you can supply only a string column
        value for lookup (the table will auto-populate from the
        selection, or you can supply a model and column name (
        used in the join operation).
        
        :param      *args           <tuple>
                    
                    #. None
                    #. <str> columnName
                    #. <subclass of Table>
                    #. (<subclass of Table> table,<str> columnName)
                    
        :param      **options       <dict> options for the query.
        
                    *. op               <Query.Op>
                    *. value            <variant>
                    *. caseSensitive    <bool>
        
        """
        # initialized with (table,column,)
        if len(args) == 2:
            self._table      = args[0]
            self._columnName = str(args[1])
        
        # initialized with (table,)
        elif len(args) == 1 and orb.Table.typecheck(args[0]):
            # when only a table is supplied, auto-use the primary key
            self._table      = args[0]
            
            pcols = args[0].schema().primaryColumns()
            if pcols:
                self._columnName = pcols[0].fieldName()
            else:
                self._columnName = None
        
        # initialized with (column,)
        elif len(args) == 1:
            self._table      = None
            self._columnName = str(args[0])
        
        # initialized with nothing
        else:
            self._table      = None
            self._columnName = None
        
        self._name          = str(options.get('name', ''))
        self._op            = options.get('op',    Query.Op.Is)
        self._value         = options.get('value', Query.UNDEFINED)
        self._caseSensitive = options.get('caseSensitive', False)
        self._negate        = options.get('negate', False)
        self._functions     = options.get('functions', [])
        self._offsetType    = options.get('offsetType', 0)
        self._offsetValue   = options.get('offsetValue', None)
    
    # operator methods
    def __add__(self, value):
        """
        Sets the offset value for this query to the inputed query with
        the And offset type.
        
        :param      value | <variant>
        
        :return     <Query> self
        """
        return self.offset(Query.OffsetType.Add, value)
    
    def __abs__(self):
        """
        Creates an absolute version of this query using the standard python
        absolute method.
        
        :return     <Query>
        """
        q = self.copy()
        q.addFunction(Query.Function.Abs)
        return q
    
    def __and__(self, other):
        """
        Creates a new compound query using the 
        QueryCompound.Op.And type.
        
        :param      other   <Query> || <QueryCompound>
        
        :return     <QueryCompound>
        
        :sa         and_
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = (Q('test') != 1) & (Q('name') == 'Eric')
                    |>>> print query
                    |(test is not 1 and name is Eric)
        """
        if Query.typecheck(other) or QueryCompound.typecheck(other):
            return self.and_(other)
        else:
            return self.offset(Query.OffsetType.And, other)
    
    def __cmp__(self, other):
        """
        Use the compare method to be able to see if two query items are
        the same vs. ==, since == is used to set the query's is value.
        
        :param      other       <variant>
        
        :return     <int> 1 | 0 | -1
        """
        if not isinstance(other, Query):
            return -1
        
        # returns 0 if these are the same item
        if id(self) == id(other):
            return 0
        return 1
        
    def __div__(self, value):
        """
        Sets the offset value for this query to the inputed query with
        the And offset type.
        
        :param      value | <variant>
        
        :return     <Query> self
        """
        return self.offset(Query.OffsetType.Divide, value)
    
    def __eq__(self, other):
        """
        Allows joining of values to the query by the == operator.
        If another Query instance is passed in, then it will do 
        a standard comparison.
        
        :param      other       <variant>
        
        :return     <Query>
        
        :sa         is
        
        :usage      |>>> from orb import *
                    |>>> query = Query('test') == 1 
                    |>>> print query
                    |test is 1
        """
        return self.is_(other)
    
    def __gt__(self, other):
        """
        Allows the joining of values to the query by the > 
        operator. If another Query instance is passed in, then it 
        will do a standard comparison.
        
        :param      other       <variant>
        
        :return     <Query>
        
        :sa         lessThan
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = Q('test') > 1
                    |>>> print query
                    |test greater_than 1
        """
        return self.greaterThan(other)
    
    def __ge__(self, other):
        """
        Allows the joining of values to the query by the >= 
        operator.  If another Query instance is passed in, then it 
        will do a standard comparison.
        
        :param      other       <variant>
        
        :return     <Query>
        
        :sa         greaterThanOrEqual
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = Q('test') >= 1
                    |>>> print query
                    |test <= 1
        """
        return self.greaterThanOrEqual(other)
    
    def __hash__(self):
        return hash(self.toXmlString())
    
    def __lt__(self, other):
        """
        Allows the joining of values to the query by the < 
        operator.  If another Query instance is passed in, then it 
        will do a standard comparison.
        
        :param      other       <variant>
        
        :return     <Query>
        
        :sa         lessThan
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = Q('test') < 1
                    |>>> print query
                    |test less_than 1
        """
        return self.lessThan(other)
    
    def __le__(self, other):
        """
        Allows the joining of values to the query by the <= 
        operator.  If another Query instance is passed in, then it 
        will do a standard comparison.
        
        :param      other       <variant>
        
        :return     <Query>
        
        :sa         lessThanOrEqual
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = Q('test') <= 1
                    |>>> print query
                    |test <= 1
        """
        return self.lessThanOrEqual(other)
        
    def __mul__(self, value):
        """
        Sets the offset value for this query to the inputed query with
        the And offset type.
        
        :param      value | <variant>
        
        :return     <Query> self
        """
        return self.offset(Query.OffsetType.Multiply, value)
    
    def __ne__(self, other):
        """
        Allows joining of values to the query by the != operator.
        If another Query instance is passed in, then it will do a
        standard comparison.
        
        :param      other       <variant>
        
        :return     <Query>
        
        :sa         isNot
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = Q('test') != 1
                    |>>> print query
                    |test is not 1
        """
        return self.isNot(other)
    
    def __neg__(self):
        """
        Negates the values within this query by using the - operator.
        
        :return     self
        
        :sa         negated
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = Q('test') == 1
                    |>>> print -query
                    |NOT test is 1
        """
        return self.negated()
    
    def __or__(self, other):
        """
        Creates a new compound query using the
        QueryCompound.Op.Or type.
        
        :param      other   <Query> || <QueryCompound>
        
        :return     <QueryCompound>
        
        :sa         or_
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = (Q('test') != 1) | (Q('name') == 'Eric')
                    |>>> print query
                    |(test is not 1 or name is Eric)
        """
        if Query.typecheck(other) or QueryCompound.typecheck(other):
            return self.or_(other)
        else:
            return self.offset(Query.OffsetType.Or, other)
        
    def __sub__(self, value):
        """
        Sets the offset value for this query to the inputed query with
        the And offset type.
        
        :param      value | <variant>
        
        :return     <Query> self
        """
        return self.offset(Query.OffsetType.Subtract, value)
    
    # private methods
    def __valueFromDict(self, data):
        
        typ = data.get('value_type')
        
        # restore list/tuples
        if typ in ('query', 'compound'):
            return (Query.fromDict(data['value']), True)
        
        # restore a list/tuple
        if typ in ('list', 'tuple'):
            value = []
            for subvalue in data['value']:
                subvalue, success = self.__valueFromDict(subvalue)
                if success:
                    value.append(subvalue)
            return (value, True)
        
        # restore the record
        elif typ == 'record':
            value      = data.get('value', {})
            schemaName = value.get('schema', '')
            dbName     = value.get('db', '')
            
            table = orb.Orb.instance().model(schemaName, database=dbName)
            if table:
                try:
                    record = table(int(value.get('id', '0')))
                except:
                    return (None, False)
                
                return (record, True)
            return (None, False)
        
        # restore a record set
        elif typ == 'record_set':
            value = data.get('value', [])
            schemaName = value.get('schema', '')
            dbName = value.get('db', '')
            ids = value.get('ids', [])
            
            table = orb.Orb.instance().model(schemaName, database=dbName)
            if table:
                try:
                    records = table.select(where = Query(table).in_(ids))
                except:
                    return (None, False)
                
                return (records, True)
            return (None, False)
        
        # restore date/datetime/time objects
        elif typ in ('datetime', 'date', 'time'):
            dtime = datetime.datetime.strptime(data['value'],
                                               '%Y-%m-%d %H:%M:%S')
            
            if typ == 'date':
                return (dtime.date(), True)
            elif typ == 'time':
                return (dtime.time(), True)
            else:
                return (dtime, True)
        
        # restore timedelta objects
        elif typ == 'timedelta':
            return (datetime.timedelta(0, float(data['value'])), True)
        
        # restore base types
        elif typ not in ('str', 'unicode'):
            try:
                return (eval(data['value']), True)
            except:
                return (None, False)
        
        return (data['value'], True)
    
    def __valueFromXml(self, xobject):
        if xobject is None:
            return (None, False)
        
        typ = xobject.get('type')
        
        # restore queries
        if typ in ('compound', 'query'):
            return (Query.fromXml(xobject[0]), True)
        
        # restore lists
        elif typ in ('list', 'tuple'):
            value = []
            for xsubvalue in xobject:
                subvalue, success = self.__valueFromXml(xsubvalue)
                if success:
                    value.append(subvalue)
            return (value, True)
        
        # restore the record
        elif typ == 'record':
            schemaName = xobject.get('schema', '')
            dbName     = xobject.get('db', '')
            
            table = orb.Orb.instance().model(schemaName, database=dbName)
            if table:
                try:
                    record = table(int(xobject.text))
                except:
                    return (None, False)
                
                return (record, True)
            return (None, False)
        
        # restore record sets
        elif typ == 'record_set':
            schemaName = xobject.get('schema', '')
            dbName = xobject.get('db', '')
            
            try:
                value = map(eval, xobject.text.split(','))
            except:
                return (None, False)
            
            table = orb.Orb.instance().model(schemaName, database=dbName)
            if table:
                try:
                    records = table.select(where = Query(table).in_(value))
                except:
                    return (None, False)
                
                return (records, True)
            return (None, False)

        # restore date/datetime/time objects
        elif typ in ('datetime', 'date', 'time'):
            dtime = datetime.datetime.strptime(xobject.text,
                                               '%Y-%m-%d %H:%M:%S')
            
            if typ == 'date':
                return (dtime.date(), True)
            elif typ == 'time':
                return (dtime.time(), True)
            else:
                return (dtime, True)
        
        # restore timedelta objects
        elif typ == 'timedelta':
            return (datetime.timedelta(0, float(xobject.text)), True)
        
        # restore base types
        elif typ not in ('str', 'unicode'):
            try:
                return (eval(xobject.text), True)
            except:
                return (None, False)
        
        return (xobject.text, True)
    
    def __valueToDict(self, value):
        # store a record
        if orb.Table.recordcheck(value):
            typ = 'record'
        
        # store a query
        elif Query.typecheck(value):
            typ = 'query'
        
        # store a query compound
        elif QueryCompound.typecheck(value):
            typ = 'compound'
        
        # store a recordset
        elif orb.RecordSet.typecheck(value):
            typ = 'record_set'
        
        # store a standard python object
        else:
            typ = type(value).__name__
        
        output = {}
        output['value_type'] = typ
        
        # save queries
        if typ in ('query', 'compound'):
            output['value'] = value.toDict()
        
        # save a list/tpule
        elif typ in ('list', 'tuple'):
            new_value = []
            for subvalue in value:
                new_value.append(self.__valueToDict(subvalue))
            output['value'] = new_value
        
        # save the record
        elif typ == 'record':
            data = {}
            data['schema'] = value.schema().name()
            data['db'] = value.schema().databaseName()
            data['id'] = value.primaryKey()
            
            output['value'] = data
        
        # save a record set
        elif typ == 'record_set':
            data = {}
            data['schema'] = value.table().schema().name()
            data['db'] = value.table().schema().databaseName()
            data['ids'] = value.primaryKeys()
            
            output['value'] = data
        
        # save date/datetime/time objects
        elif typ in ('datetime', 'date', 'time'):
            output['value'] = value.strftime('%Y-%m-%d %H:%M:%S')
        
        # save timedelta objects
        elif typ == 'timedelta':
            output['value'] = value.total_seconds()
        
        # save base types
        else:
            try:
                output['value'] = str(value)
            except:
                pass
            
        return output
    
    def __valueToXml(self, xparent, value):
        if orb.Table.recordcheck(value):
            typ = 'record'
        elif Query.typecheck(value):
            typ = 'query'
        elif QueryCompound.typecheck(value):
            typ = 'compound'
        elif orb.RecordSet.typecheck(value):
            typ = 'record_set'
        else:
            typ = type(value).__name__
        
        xobject = ElementTree.SubElement(xparent, 'object')
        xobject.set('type', typ)
        
        # save queries
        if typ in ('query', 'compound'):
            value.toXml(xobject)
        
        # save lists
        elif typ in ('list', 'tuple'):
            for subvalue in value:
                self.__valueToXml(xobject, subvalue)
        
        # save the record
        elif typ == 'record':
            xobject.set('schema', value.schema().name())
            xobject.set('db', value.schema().databaseName())
            xobject.text = str(value.primaryKey())
        
        # save the record set
        elif typ == 'record_set':
            xobject.set('schema', value.table().schema().name())
            xobject.set('db', value.table().schema().databaseName())
            xobject.text = ','.join(map(str, value.primaryKeys()))
        
        # save date/datetime/time objects
        elif typ in ('datetime', 'date', 'time'):
            xobject.text = value.strftime('%Y-%m-%d %H:%M:%S')
        
        # save timedelta objects
        elif typ == 'timedelta':
            xobject.text = str(value.total_seconds())
        
        # save base types
        else:
            try:
                xobject.text = str(value)
            except:
                pass
        
        return xobject
    
    # public methods
    def addFunction(self, func):
        """
        Adds a new function for this query.
        
        :param      func | <Query.Function>
        """
        self._functions.append(func)
        
    def after(self, value):
        """
        Sets the operator type to Query.Op.After and sets the value to 
        the amount that this query should be lower than.  This is functionaly
        the same as doing the lessThan operation, but is useufl for visual 
        queries for things like dates.
        
        :param      value   | <variant>
        
        :return     <Query>
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = Q('dateStart').after(date.today())
                    |>>> print query
                    |dateStart after 2011-10-10
        """
        newq = self.copy()
        newq.setOperatorType(Query.Op.After)
        newq.setValue(value)
        
        return newq
    
    def and_(self, other):
        """
        Creates a new compound query using the 
        QueryCompound.Op.And type.
        
        :param      other   <Query> || <QueryCompound>
        
        :return     <QueryCompound>
        
        :sa         __and__
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = (Q('test') != 1).and_((Q('name') == 'Eric')
                    |>>> print query
                    |(test is not 1 and name is Eric)
        """
        if ( other is None or other.isNull() ):
            return self
            
        elif ( self.isNull() ):
            return other
        
        return QueryCompound(self, other, op = QueryCompound.Op.And)
    
    def before(self, value):
        """
        Sets the operator type to Query.Op.Before and sets the value to 
        the amount that this query should be lower than.  This is functionaly
        the same as doing the lessThan operation, but is useufl for visual 
        queries for things like dates.
        
        :param      value   | <variant>
        
        :return     <Query>
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = Q('dateStart').before(date.today())
                    |>>> print query
                    |dateStart before 2011-10-10
        """
        newq = self.copy()
        newq.setOperatorType( Query.Op.Before )
        newq.setValue(value)
        
        return newq
    
    def between(self, valueA, valueB):
        """
        Sets the operator type to Query.Op.Between and sets the
        value to a tuple of the two inputed values.
        
        :param      valueA      <variant>
        :param      valueB      <variant>
        
        :return     <Query>
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = Q('test').between(1,2)
                    |>>> print query
                    |test between [1,2]
        """
        newq = self.copy()
        newq.setOperatorType( Query.Op.Between )
        newq.setValue([valueA, valueB])
        
        return newq
    
    def caseSensitive(self):
        """
        Returns whether or not this query item will be case
        sensitive.  This will be used with string lookup items.
        
        :return     <bool>
        """
        return self._caseSensitive
    
    def column(self, schema=None, traversal=None):
        """
        Returns the column instance for this query.
        
        :return     <orb.Column> || <tuple> (primary key column dictionary)
        """
        if not self._columnName and self._table:
            cols = self._table.schema().primaryKeyColumns()
            if not cols:
                return None
            return cols[0]
        elif self._table:
            return self._table.schema().column(self._columnName,
                                               traversal=traversal)
        elif schema:
            return schema.column(self._columnName, traversal=traversal)
        return None
    
    def columns(self, schema=None):
        """
        Returns any columns used within this query.
        
        :return     [<orb.Column>, ..]
        """
        output = []
        column = self.column(schema=schema, traversal=output)
        if column:
            output.append(column)
        
        # include any columns related to the value
        if type(self._value) not in (list, set, tuple):
            value = (self._value,)
        else:
            value = self._value
        
        for val in value:
            if Query.typecheck(val) or QueryCompound.typecheck(val):
                output += val.columns(schema=schema)
        
        return list(set(output))
    
    def columnName(self):
        """
        Reutrns the column name that this query instance is
        looking up.
        
        :return     <str>
        """
        return self._columnName
    
    def contains(self, value, caseSensitive=False):
        """
        Sets the operator type to Query.Op.Contains and sets the    
        value to the inputd value.  Use an asterix for wildcard
        characters.
        
        :param      value           <variant>
        :param      caseSensitive   <bool>
        
        :return     self    (useful for chaining)
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = Q('comments').contains('test')
                    |>>> print query
                    |comments contains test
        """
        newq = self.copy()
        newq.setOperatorType( Query.Op.Contains )
        newq.setValue(value)
        newq.setCaseSensitive( caseSensitive )
        
        return newq
    
    def copy(self):
        """
        Returns a duplicate of this instance.
        
        :return     <Query>
        """
        out = Query()
        out._table      = self._table
        out._columnName = self._columnName
        out._name = self._name
        out._op = self._op
        out._value = self._value
        out._caseSensitive = self._caseSensitive
        out._negate = self._negate
        out._functions = self._functions[:]
        out._offsetType = self._offsetType
        out._offsetValue = self._offsetValue
        return out
    
    def doesNotContain(self, value):
        """
        Sets the operator type to Query.Op.DoesNotContain and sets the
        value to the inputed value.
        
        :param      value       <variant>
        
        :return     self    (useful for chaining)
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = Q('comments').doesNotContain('test')
                    |>>> print query
                    |comments does_not_contain test
        """
        newq = self.copy()
        newq.setOperatorType( Query.Op.DoesNotContain )
        newq.setValue( value )
        
        return newq
    
    def doesNotMatch(self, value):
        """
        Sets the operator type to Query.Op.DoesNotMatch and sets the \
        value to the inputed value.
        
        :param      value       <variant>
        
        :return     self    (useful for chaining)
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = Q('comments').doesNotMatch('test')
                    |>>> print query
                    |comments does_not_contain test
        """
        newq = self.copy()
        newq.setOperatorType( Query.Op.DoesNotMatch )
        newq.setValue( value )
        
        return newq
    
    def endswith(self, value):
        """
        Sets the operator type to Query.Op.Endswith and sets \
        the value to the inputed value.  This method will only work on text \
        based fields.
        
        :param      value       <str>
        
        :return     <Query>
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = Q('test').endswith('blah')
                    |>>> print query
                    |test startswith blah
        """
        newq = self.copy()
        newq.setOperatorType(Query.Op.Endswith)
        newq.setValue(value)
        
        return newq
    
    def expandShortcuts(self, basetable=None):
        """
        Expands any shortcuts that were created for this query.  Shortcuts
        provide the user access to joined methods using the '.' accessor to
        access individual columns for referenced tables.
        
        :param      basetable | <orb.Table> || None
        
        :usage      |>>> from orb import Query as Q
                    |>>> # lookup the 'username' of foreign key 'user'
                    |>>> Q('user.username') == 'bob.smith'
        
        :return     <orb.Query> || <orb.QueryCompound>
        """
        # look for shortcuts
        if not '.' in self.columnName():
            return self
        
        # lookup the table for this query
        table = self.table()
        if not table:
            table = basetable
        
        if not table:
            raise errors.MissingTableShortcut(self)
        
        # setup the shortcut pathing
        names = self.columnName().split('.')
        compound = Query()
        for i, name in enumerate(names):
            column = table.schema().column(name)
            if not column:
                return Query()
            
            # for the last column, that is the value we are trying to access
            if i == len(names) - 1:
                final = self.copy()
                final.setTable(table)
                final.setColumnName(name)
                
                compound &= final
            
            # otherwise, we are going through a join to access it
            else:
                ref_table = column.referenceModel()
                if not ref_table:
                    return Query()
                
                compound &= Query(table, name) == Query(ref_table)
            
            table = ref_table
        
        return compound
    
    def findValue(self, column, instance=1):
        """
        Looks up the value for the inputed column name for the given instance.
        If the instance == 1, then this result will return the value and a
        0 instance count, otherwise it will decrement the instance for a
        matching column to indicate it was found, but not at the desired
        instance.
        
        :param      column   | <str>
                    instance | <int>
        
        :return     (<bool> success, <variant> value, <int> instance)
        """
        if not column == self.columnName():
            return (False, None, instance)
        
        elif instance > 1:
            return (False, None, instance-1)
        
        return (True, self.value(), 0)
    
    def functions(self):
        """
        Returns a list of the functions that are associated with this query.
        This will modify the lookup column for the given function type in order.
        
        :return     [<Query.Function>, ..]
        """
        return self._functions
    
    def functionNames(self):
        """
        Returns the text for the functions associated with this query.
        
        :return     [<str>, ..]
        """
        return map(Query.Function.__getitem__, self.functions())
    
    def is_(self, value):
        """
        Sets the operator type to Query.Op.Is and sets the
        value to the inputed value.
        
        :param      value       <variant>
        
        :return     <Query>
        
        :sa         __eq__
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = Q('test').is_(1)
                    |>>> print query
                    |test is 1
        """
        newq = self.copy()
        newq.setOperatorType(Query.Op.Is)
        newq.setValue(value)
        
        return newq
    
    def greaterThan(self, value):
        """
        Sets the operator type to Query.Op.GreaterThan and sets the
        value to the inputed value.
        
        :param      value       <variant>
        
        :return     <Query>
        
        :sa         __gt__
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = Q('test').greaterThan(1)
                    |>>> print query
                    |test greater_than 1
        """
        newq = self.copy()
        newq.setOperatorType(Query.Op.GreaterThan)
        newq.setValue(value)
        
        return newq
    
    def greaterThanOrEqual(self, value):
        """
        Sets the operator type to Query.Op.GreaterThanOrEqual and 
        sets the value to the inputed value.
        
        :param      value       <variant>
        
        :return     <Query>
        
        :sa         __ge__
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = Q('test').greaterThanOrEqual(1)
                    |>>> print query
                    |test greater_than_or_equal 1
        """
        newq = self.copy()
        newq.setOperatorType(Query.Op.GreaterThanOrEqual)
        newq.setValue(value)
        
        return newq
    
    def hasShortcuts(self):
        """
        Returns whether or not this widget has shortcuts.
        
        :return     <bool>
        """
        return '.' in self.columnName()
    
    def isNegated(self):
        """
        Returns whether or not this query is negated.
        
        :return <bool>
        """
        return self._negate
    
    def isNot(self, value):
        """
        Sets the operator type to Query.Op.IsNot and sets the
        value to the inputed value.
        
        :param      value       <variant>
        
        :return     <Query>
        
        :sa         __ne__
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = Q('test').isNot(1)
                    |>>> print query
                    |test is not 1
        """
        newq = self.copy()
        newq.setOperatorType(Query.Op.IsNot)
        newq.setValue(value)
        
        return newq
    
    def isNull(self):
        """
        Return whether or not this query contains any information.
        
        :return     <bool>
        """
        if self._columnName or self._value != Query.UNDEFINED:
            return False
        return True
    
    def isOffset(self):
        """
        Returns whether or not this query is offset.
        
        :return     <bool>
        """
        return self._offsetType != 0
    
    def isUndefined(self):
        """
        Return whether or not this query contains undefined value data.
        
        :return <bool>
        """
        return self._value == Query.UNDEFINED
    
    def in_(self, value):
        """
        Sets the operator type to Query.Op.IsIn and sets the value
        to the inputed value.
        
        :param      value       <variant>
        
        :return     <Query>
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = Q('test').isIn([1,2])
                    |>>> print query
                    |test is_in [1,2]
        """
        newq = self.copy()
        newq.setOperatorType(Query.Op.IsIn)
        
        # convert a set to a list
        if type(value) == set:
            value = list(value)
        
        # convert value to a list
        if type(value) not in (list, tuple) and \
           not orb.RecordSet.typecheck(value):
            value = [value]
        
        newq.setValue(value)
        
        return newq
    
    def name(self):
        """
        Returns the optional name for this query.
        
        :return     <str>
        """
        return self._name
    
    def notIn(self, value):
        """
        Sets the operator type to Query.Op.IsNotIn and sets the value
        to the inputed value.
        
        :param      value       <variant>
        
        :return     <Query>
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = Q('test').not_in([1,2])
                    |>>> print query
                    |test is_not_in [1,2]
        """
        newq = self.copy()
        newq.setOperatorType(Query.Op.IsNotIn)
        
        if type(value) == set:
            value = list(value)
        
        if type(value) not in (list, tuple):
            value = [value]
        
        newq.setValue( value )
        
        return newq
    
    def lessThan(self, value):
        """
        Sets the operator type to Query.Op.LessThan and sets the
        value to the inputed value.
        
        :param      value       <variant>
        
        :return     <Query>
        
        :sa         lessThan
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = Q('test').lessThan(1)
                    |>>> print query
                    |test less_than 1
        """
        newq = self.copy()
        newq.setOperatorType(Query.Op.LessThan)
        newq.setValue(value)
        
        return newq
    
    def lessThanOrEqual(self, value):
        """
        Sets the operator type to Query.Op.LessThanOrEqual and sets 
        the value to the inputed value.
        
        :param      value       <variant>
        
        :return     <Query>
        
        :sa         lessThanOrEqual
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = Q('test').lessThanOrEqual(1)
                    |>>> print query
                    |test less_than_or_equal 1
        """
        newq = self.copy()
        newq.setOperatorType( Query.Op.LessThanOrEqual )
        newq.setValue(value)
        
        return newq
    
    def lower(self):
        """
        Returns a new query for this instance with Query.Function.Lower as
        a function option.
        
        :return     <Query>
        """
        q = self.copy()
        q.addFunction(Query.Function.Lower)
        return q
    
    def matches(self, value):
        """
        Sets the operator type to Query.Op.Matches and sets \
        the value to the inputed regex expression.  This method will only work \
        on text based fields.
        
        :param      value       <str>
        
        :return     <Query>
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = Q('test').matches('^\d+-\w+$')
                    |>>> print query
                    |test matches ^\d+-\w+$
        """
        newq = self.copy()
        newq.setOperatorType(Query.Op.Matches)
        newq.setValue(value)
        
        return newq
    
    def negated(self):
        """
        Negates the current state for this query.
        
        :return     <self>
        """
        query = self.copy()
        query.setOperatorType(self.operatorType())
        query.setValue(self.value())
        query._negate = not self._negate
        return query
    
    def offset(self, offsetType, value):
        """
        Assigns a query offset value for the given type.  The value can
        be either static, or another query that will dynamically calculate
        during the database query.
        
        :param      offsetType | <Query.OffsetType>
                    value      | <variant>
        """
        self._offsetType = offsetType
        self._offsetValue = value
        
        return self
    
    def offsetType(self):
        """
        Returns the offset type for this query.
        
        :return     <Query.OffsetType>
        """
        return self._offsetType
    
    def offsetValue(self):
        """
        Returns the offset value for this query.
        
        :return     <variant>
        """
        return self._offsetValue
    
    def operatorType(self):
        """
        Returns the operator type assigned to this query
        instance.
        
        :return     <Query.Op>
        """
        return self._op
    
    def or_(self, other):
        """
        Creates a new compound query using the 
        QueryCompound.Op.Or type.
        
        :param      other   <Query> || <QueryCompound>
        
        :return     <QueryCompound>
        
        :sa         or_
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = (Q('test') != 1).or_(Q('name') == 'Eric')
                    |>>> print query
                    |(test does_not_equal 1 or name is Eric)
        """
        if ( other is None or other.isNull() ):
            return self
            
        elif ( self.isNull() ):
            return other
        
        return QueryCompound(self, other, op = QueryCompound.Op.Or)
    
    def removed(self, columnName):
        """
        Removes the query containing the inputed column name from this
        query set.
        
        :param      columnName | <str>
        
        :return     <Query>
        """
        if self.columnName() == columnName:
            return Query()
        return self
    
    def schema(self):
        """
        Returns the schema associated with this query.
        
        :return     <orb.TableSchema> || None
        """
        table = self.table()
        if table:
            return table.schema()
        return None
    
    def schemas(self):
        """
        Returns the schemas associated with this query.
        
        :return     [<orb.TableSchema>, ..]
        """
        return map(lambda x: x.schema(), self.tables())
    
    def setCaseSensitive(self, state):
        """
        Sets whether or not this query will be case sensitive.
        
        :param      state   <bool>
        """
        self._caseSensitive = state
    
    def setColumnName(self, columnName):
        """
        Sets the column name used for this query instance.
        
        :param      columnName      <str>
        """
        self._columnName = str(columnName)
    
    def setOperatorType(self, op):
        """
        Sets the operator type used for this query instance.
        
        :param      op          <Query.Op>
        """
        self._op = op
    
    def setName(self, name):
        """
        Sets the optional name for this query to the given name.
        
        :param      name | <str>
        """
        self._name = name
    
    def setTable(self, table):
        """
        Sets the table instance that is being referenced for this query.
        
        :param      table | <subclass of orb.Table>
        """
        self._table = table
    
    def setValue(self, value):
        """
        Sets the value that will be used for this query instance.
        
        :param      value       <variant>
        """
        self._value = value
    
    def setValueString(self, valuestring):
        """
        Sets the value for this query from the inputed string representation \
        of the value.  For this method to work, the table and column name for 
        this query needs to be set.  Otherwise, the string value will be used.
        
        :param      valuestring | <str>
        """
        column = self.column()
        if ( column ):
            self.setValue(column.valueFromString(valuestring))
        else:
            self.setValue(valuestring)
    
    def startswith(self, value):
        """
        Sets the operator type to Query.Op.Startswith and sets \
        the value to the inputed value.  This method will only work on text \
        based fields.
        
        :param      value       <str>
        
        :return     <Query>
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = Q('test').startswith('blah')
                    |>>> print query
                    |test startswith blah
        """
        newq = self.copy()
        newq.setOperatorType( Query.Op.Startswith )
        newq.setValue( value )
        
        return newq
    
    def table(self):
        """
        Return the table instance that this query is referencing.
        
        :return     <subclass of Table> || None
        """
        return self._table
    
    def tables(self):
        """
        Returns the tables that this query is referencing.
        
        :return     [ <subclass of Table>, .. ]
        """
        output = set()
        if self._table:
            output.add(self._table)
        
        if type(self._value) not in (list, set, tuple):
            value = (self._value,)
        else:
            value = self._value
        
        for val in value:
            if Query.typecheck(val) or QueryCompound.typecheck(val):
                output.update(val.tables())
        
        return list(output)
    
    def toDict(self):
        """
        Creates a dictionary representation of this query.
        
        :return     <dict>
        """
        output = {}
        
        if self.isNull():
            return output
        
        output['type']          = 'query'
        output['name']          = self._name
        output['op']            = self._op
        output['caseSensitive'] = self._caseSensitive
        output['negated']       = self._negate
        output['column']        = self._columnName
        
        table = self._table
        if table:
            output['schema']    = table.schema().name()
            output['db']        = table.schema().databaseName()
        
        value_dict = self.__valueToDict(self._value)
        output.update(value_dict)
        
        # store the offset information
        if self.isOffset():
            offset = {}
            offset['type'] = self.offsetType()
            value_dict = self.__valueToDict(self.offsetValue())
            offset.update(value_dict)
        
        return output
    
    def toString(self):
        """
        Returns this query instance as a semi readable language
        query.
        
        :warning    This method will NOT return a valid SQL statement.  The
                    backend classes will determine how to convert the Query
                    instance to whatever lookup code they need it to be.
        
        :return     <str>
        """
        if not self.__nonzero__():
            return ''
            
        pattern = dict(Query.SyntaxPatterns)[self.operatorType()]
        column  = self.columnName()
        val     = self.value()
        
        if self.table():
            column = '%s.%s' % (self.table().__name__, column)
        
        otype = self.offsetType()
        symbol = Query.OffsetSymbol.get(otype)
        if symbol:
            column = '(' + column + symbol + str(self.offsetValue()) + ')'
        
        if val == Query.UNDEFINED:
            return column
        
        opts = {'field': column, 'value': val}
        return pattern.syntax() % opts
    
    def toXml(self, xparent=None):
        """
        Returns this query as an XML value.
        
        :param      xparent | <xml.etree.ElementTree.Element> || None
        
        :return     <xml.etree.ElementTree.Element>
        """
        if self.isNull():
            return None
        
        if xparent is None:
            xquery = ElementTree.Element('query')
        else:
            xquery = ElementTree.SubElement(xparent, 'query')
        
        xquery.set('name', str(self._name))
        xquery.set('op', str(self._op))
        xquery.set('caseSensitive', str(self._caseSensitive))
        xquery.set('negated', str(self._negate))
        xquery.set('column', str(self._columnName))
        
        table = self._table
        if table:
            xquery.set('schema', table.schema().name())
            xquery.set('db', table.schema().databaseName())
        
        self.__valueToXml(xquery, self._value)
        
        if self.isOffset():
            xoffset = ElementTree.SubElement(xquery, 'offset')
            xoffset.set('type', str(self.offsetType()))
            self.__valueToXml(xoffset, self.offsetValue())
        
        return xquery
    
    def toXmlString(self, indented=False):
        """
        Returns this query as an XML string.
        
        :param      indented | <bool>
        
        :return     <str>
        """
        xml = self.toXml()
        if xml is None:
            return ''
        
        if indented:
            projex.text.xmlindent(xml)
        
        return ElementTree.tostring(xml)
    
    def upper(self):
        """
        Returns this query with the Upper function added to its list.
        
        :return     <Query>
        """
        q = self.copy()
        q.addFunction(Query.Function.Upper)
        return q
    
    def validate(self, record):
        """
        Validates this query's value against the inputed record.  This will 
        return True if the record satisies the query condition.
        
        :param      record | <
        
        :return     <bool>
        """
        if isinstance(record, orb.Table):
            rvalue = record.recordValue(self._columnName, autoInflate=False)
        else:
            rvalue = record.get(self._columnName)
        
        mvalue = self._value
        
        if orb.Table.recordcheck(mvalue):
            mvalue = mvalue.primaryKey()
        if orb.Table.recordcheck(rvalue):
            rvalue = rvalue.primaryKey()
        
        # basic operations
        if self._op == Query.Op.Is:
            return rvalue == mvalue
        
        elif self._op == Query.Op.IsNot:
            return rvalue != mvalue
        
        # comparison operations
        elif self._op == Query.Op.Between:
            if len(mvalue) == 2:
                return mvalue[0] < rvalue < mvalue[1]
            return False
        
        elif self._op == Query.Op.LessThan:
            return rvalue < mvalue
        
        elif self._op == Query.Op.LessThanOrEqual:
            return rvalue <= mvalue
        
        elif self._op == Query.Op.GreaterThan:
            return rvalue > mvalue
        
        elif self._op == Query.Op.GreaterThanOrEqual:
            return rvalue >= mvalue
        
        # string operations
        elif self._op == Query.Op.Contains:
            return projex.text.encoded(rvalue) in projex.text.encoded(mvalue)
        
        elif self._op == Query.Op.DoesNotContain:
            return not projex.text.encoded(rvalue) in projex.text.encoded(mvalue)
        
        elif self._op == Query.Op.Startswith:
            encoded = projex.text.encoded(mvalue)
            return projex.text.encoded(rvalue).startswith(encoded)
        
        elif self._op == Query.Op.Endswith:
            encoded = projex.text.encoded(mvalue)
            return projex.text.encoded(rvalue).endswith(encoded)
        
        elif self._op == Query.Op.Matches:
            return re.match(projex.text.encoded(mvalue),
                            projex.text.encoded(rvalue)) != None
        
        elif self._op == Query.Op.DoesNotMatch:
            return re.match(projex.text.encoded(mvalue),
                            projex.text.encoded(rvalue)) == None
        
        # list operations
        elif self._op == Query.Op.IsIn:
            return rvalue in mvalue
        
        elif self._op == Query.Op.IsNotIn:
            return rvalue not in mvalue
        
        return False
    
    def value(self):
        """
        Returns the value for this query instance
        
        :return     <variant>
        """
        return self._value
    
    def valueString(self):
        """
        Converts the data for this query to a string value and returns it.  For
        this method to properly work, you need to have the columnName and table
        set for this query.
        
        :return     <str>
        """
        column = self.column()
        if ( column ):
            return column.valueToString(self.value())
        
        return projex.text.encoded(self.value())
    
    @staticmethod
    def fromDict(data):
        """
        Restores a query from the inputed data dictionary representation.
        
        :param      data | <str>
        
        :return     <Query>
        """
        if data.get('type') == 'compound':
            return QueryCompound.fromDict(data)
        
        out = Query()
        out._name = data.get('name', '')
        out._op = int(data.get('op', '1'))
        out._caseSensitive = str(data.get('caseSensitive')).lower() == 'true'
        out._negated = str(data.get('negated')).lower() == 'true'
        out._columnName = str(data.get('column', ''))
        
        schema = data.get('schema', '')
        if schema:
            dbname = data.get('db', '')
            out._table = orb.Orb.instance().model(schema, database=dbname)
        
        # restore the value from the dictionary
        value, success = out.__valueFromDict(data)
        if success:
            out._value = value
        
        # restore the offset
        offset = data.get('offset')
        if offset is not None:
            typ = int(offset.get('type', 0))
            value, success = out.__valueFromDict(offset)
            if success:
                out._offsetValue = value
        
        return out
    
    @staticmethod
    def fromSearch(searchstr, mode=SearchMode.All, schema=None):
        """
        Creates a query instance from a particular search string.  Search 
        strings are a custom way of defining short hand notation search syntax.
        
        :param      searchstr | <str>
                    mode      | <orb.SearchMode>
        
        :return     ([<str> keyword, ..], <Query> query)
        
        :syntax     no deliminator (testing test test) | search keywords
                    column:value                       | column contains value
                    column:*value                      | column endswith value
                    column:value*                      | column startswith value
                    column:"value"                     | column == value
                    column:<value                      | column < value
                    column:<=value                     | column <= value
                    column:a<b                         | column between a and b
                    column:>value                      | column > value
                    column:>=value                     | column >= value
                    column:!value                      | column negate value
        """
        searchstr = projex.text.encoded(searchstr)
        search_re = re.compile('([\w\.]+):([^\s]+|"[^"]+")')
        results   = search_re.search(searchstr)
        query     = Query()
        
        def eval_value(value):
            result = re.match('^' + projex.regex.DATETIME + '$', value)
            
            # convert a datetime value
            if result:
                data = result.groupdict()
                if len(data['year']):
                    data['year'] = '20' + data['year']
                
                if not data['second']:
                    data['second'] = '0'
                
                if data['ap'].startswith('p'):
                    data['hour'] = 12 + int(data['hour'])
                
                return datetime.datetime(int(data['year']),
                                         int(data['month']),
                                         int(data['day']),
                                         int(data['hour']),
                                         int(data['min']),
                                         int(data['second']))
            
            # convert a date value
            result = re.match('^' + projex.regex.DATE + '$', value)
            if result:
                data = result.groupdict()
                if len(data['year']):
                    data['year'] = '20' + data['year']
                
                return datetime.date(int(data['year']),
                                     int(data['month']),
                                     int(data['day']))
            
            # convert a time value
            result = re.match('^' + projex.regex.TIME + '$', value)
            if result:
                data = result.groupdict()
                if not data['second']:
                    data['second'] = '0'
                
                if data['ap'].startswith('p'):
                    data['hour'] = 12 + int(data['hour'])
                
                return datetime.time(int(data['hour']),
                                     int(data['min']),
                                     int(data['second']))
            
            try:
                return eval(value)
            except:
                return value
            
        while results:
            column, values = results.groups()
            values = values.strip()
            
            if schema:
                col = schema.column(column)
            else:
                col = None
            
            # see if this is an exact value
            if values.startswith('"') and values.endswith('"'):
                query &= Q(column) == values.strip('"')
            
            # process multiple values
            all_values = values.split(',')
            sub_q = Query()
            
            for value in all_values:
                value = value.strip()
                
                # process a contains search (same as no asterixes)
                if value.startswith('*') and value.endswith('*'):
                    value = value.strip('*')
                
                if not value:
                    continue
                
                negate = False
                if value.startswith('!'):
                    negate = True
                
                if value.startswith('*'):
                    sub_q |= Query(column).startswith(value.strip('*'))
                
                elif value.endswith('*'):
                    sub_q |= Query(column).endswith(value.strip('*'))
                
                elif value.startswith('<='):
                    value = eval_value(value[2:])
                    sub_q |= Query(column) <= value
                
                elif value.startswith('<'):
                    value = eval_value(value[1:])
                    sub_q |= Query(column) < value
                
                elif value.startswith('>='):
                    value = eval_value(value[2:])
                    sub_q |= Query(column) >= value
                
                elif value.startswith('>'):
                    value = eval_value(value[1:])
                    sub_q |= Query(column) > value
                
                elif '<' in value or '-' in value:
                    try:
                        a, b = value.split('<')
                        success = True
                    except ValueError:
                        success = False
                    
                    if not success:
                        try:
                            a, b = value.split('-')
                            success = True
                        except ValueError:
                            success = False
                    
                    if success:
                        a = eval_value(a)
                        b = eval_value(b)
                        
                        sub_q |= Query(column).between(a, b)
                        
                    else:
                        sub_q |= Query(column).contains(value)
                
                else:
                    # process additional options
                    if not (col and col.isString()):
                        value = eval_value(value)
                    
                    if not isinstance(value, basestring):
                        sub_q |= Query(column) == value
                    else:
                        sub_q |= Query(column).contains(value)
            
            if mode == SearchMode.All:
                query &= sub_q
            else:
                query |= sub_q
            
            # update the search values
            searchstr = searchstr[:results.start()] + searchstr[results.end():]
            results   = search_re.search(searchstr)
        
        return (searchstr.split(), query)
    
    @staticmethod
    def fromString(querystr):
        """
        Recreates a query instance from the inputed string value.
        
        :param      querystr | <str>
        
        :return     <Query> || <QueryCompound> || None
        """
        querystr = projex.text.encoded(querystr)
        
        queries  = {}
        for op, pattern in Query.SyntaxPatterns:
            pattern = pattern.pattern()
            match   = pattern.search(querystr)
            
            while ( match ):
                # extract query information
                key  = 'QUERY_%i' % (len(queries) + 1)
                grp  = match.group()
                data = match.groupdict()
                
                # built the new query instance
                value = data['value']
                if ( op in (Query.Op.IsIn, Query.Op.IsNotIn) ):
                    value = map(lambda x: x.strip(), 
                                data['value'].strip('[]').split(','))
                
                query = Query(data['field'], op = op, value = value)
                queries[key] = query
                
                # replace the querystr with a pointer to this query for 
                # future use
                querystr = querystr.replace(grp, key)
                match    = pattern.search(querystr)
        
        # if only 1 query existed, then no need to create a compound
        if (len(queries) == 1 ):
            return queries.values()[0]
        
        # otherwise, we need to build a compound
        return QueryCompound.build(querystr, queries)
    
    @staticmethod
    def fromXml(xquery):
        if xquery.tag == 'compound':
            return QueryCompound.fromXml(xquery)
        
        out = Query()
        out._name = xquery.get('name', '')
        out._op = int(xquery.get('op', '1'))
        out._caseSensitive = xquery.get('caseSensitive') == 'True'
        out._negated = xquery.get('negated') == 'True'
        out._columnName = xquery.get('column', '')
        
        schema = xquery.get('schema')
        if schema:
            dbname = xquery.get('db', '')
            out._table = orb.Orb.instance().model(schema, database=dbname)
        
        value, success = out.__valueFromXml(xquery.find('object'))
        if success:
            out._value = value
        
        xoffset = xquery.get('offset')
        if xoffset is not None:
            typ = int(xoffset.get('type', '0'))
            value, success = out.__valueFromXml(xoffset)
            if success:
                out._offsetValue = value
        
        return out
    
    @staticmethod
    def fromXmlString(xquery_str):
        """
        Returns a query from the XML string.
        
        :param      xquery_str | <str>
        
        :return     <orb.Query> || <orb.QueryCompound>
        """
        if not xquery_str:
            return Query()
        
        try:
            xml = ElementTree.fromstring(xquery_str)
        except ExpatError:
            return Query()
        
        return Query.fromXml(xml)
    
    @staticmethod
    def typecheck(obj):
        """
        Returns whether or not the inputed object is a type of a query.
        
        :param      obj     <variant>
        
        :return     <bool>
        """
        return isinstance(obj, Query)
    
    @staticmethod
    def testNull(query):
        """
        Tests to see if the inputed query is null.  This will also check
        against None and 0 values.
        
        :param      query | <orb.Query> || <orb.QueryCompound> || <variant>
        """
        if Query.typecheck(query) or QueryCompound.typecheck(query):
            return query.isNull()
        return True
    
    #----------------------------------------------------------------------
    #                       QUERY AGGREGATE DEFINITIONS
    #----------------------------------------------------------------------
    @staticmethod
    def COUNT(table, **options):
        """
        Defines a query for generating a count for a given record set.
        
        :param      recordset | <orb.RecordSet>
        
        :return     <orb.QueryAggregate>
        """
        return QueryAggregate('count', table, **options)
    
    @staticmethod
    def MAX(table, **options):
        """
        Defines a query for generating a maximum value for the given recordset.
        
        :param      recordset | <orb.RecordSet>
        
        :return     <orb.QueryAggregate>
        """
        return QueryAggregate('max', **options)
    
    @staticmethod
    def MIN(table, **options):
        """
        Defines a query for generating a maximum value for the given recordset.
        
        :param      recordset | <orb.RecordSet>
        
        :return     <orb.QueryAggregate>
        """
        return QueryAggregate('min', table, **options)
    
    @staticmethod
    def SUM(table, **options):
        """
        Defines a query for generating a sum for the given recordset.
        
        :param      recordset | <orb.RecordSet>
        
        :return     <orb.QueryAggregate>
        """
        return QueryAggregate('sum', table, **options)

#------------------------------------------------------------------------------

class QueryCompound(object):
    """ Defines combinations of queries via either the AND or OR mechanism. """
    Op = enum(
        'And',
        'Or'
    )
    
    def __contains__(self, value):
        """
        Returns whether or not the query compound contains a query for the
        inputed column name.
        
        :param      value | <variant>
        
        :return     <bool>
        
        :usage      |>>> from orb import Query as Q
                    |>>> q = Q('testing') == True
                    |>>> 'testing' in q
                    |True
                    |>>> 'name' in q
                    |False
        """
        for query in self._queries:
            if value in query:
                return True
        return False
    
    def __nonzero__(self):
        return not self.isNull()
    
    def __str__(self):
        """
        Returns the string representation for this query instance
        
        :sa         toString
        """
        return self.toString()
        
    def __init__(self, *queries, **options):
        self._queries   = queries
        self._op        = options.get('op', QueryCompound.Op.And)
        self._negate    = options.get('negate', False)
        self._name      = str(options.get('name', ''))
    
    def __and__(self, other):
        """
        Creates a new compound query using the 
        QueryCompound.Op.And type.
        
        :param      other   <Query> || <QueryCompound>
        
        :return     <QueryCompound>
        
        :sa         and_
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = (Q('test') != 1) & (Q('name') == 'Eric')
                    |>>> print query
                    |(test does_not_equal 1 and name is Eric)
        """
        return self.and_(other)
    
    def __hash__(self):
        return hash(self.toXmlString())
    
    def __neg__(self):
        """
        Negates the current state of the query.
        
        :sa     negate
        
        :return     self
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = (Q('test') == 1) & (Q('name') == 'Eric')
                    |>>> print -query
                    |NOT (test is  1 and name is Eric)
        """
        return self.negated()
    
    def __or__(self, other):
        """
        Creates a new compound query using the 
        QueryCompound.Op.Or type.
        
        :param      other   <Query> || <QueryCompound>
        
        :return     <QueryCompound>
        
        :sa         or_
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = (Q('test') != 1) | (Q('name') == 'Eric')
                    |>>> print query
                    |(test isNot 1 or name is Eric)
        """
        return self.or_(other)
        
    def and_(self, other):
        """
        Creates a new compound query using the 
        QueryCompound.Op.And type.
        
        :param      other   <Query> || <QueryCompound>
        
        :return     <QueryCompound>
        
        :sa         __and__
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = (Q('test') != 1).and_((Q('name') == 'Eric')
                    |>>> print query
                    |(test isNot 1 and name is Eric)
        """
        if other is None or other.isNull():
            return self
        
        elif self.isNull():
            return other
        
        # grow this objects list if the operator types are the same
        if self.operatorType() == QueryCompound.Op.And and \
           not self.isNegated():
            queries = list(self._queries)
            queries.append(other)
            opts = { 'op': QueryCompound.Op.And }
            
            # pylint: disable-msg=W0142
            return QueryCompound( *queries, **opts )
            
        # create a new compound
        return QueryCompound(self, other, op = QueryCompound.Op.And)
    
    def copy(self):
        """
        Returns a copy of this query compound.
        
        :return     <QueryCompound>
        """
        out = QueryCompound()
        out._queries = [q.copy() for q in self._queries]
        out._op      = self._op
        out._negate  = self._negate
        return out
    
    def columns(self, schema=None):
        """
        Returns any columns used within this query.
        
        :return     [<orb.Column>, ..]
        """
        output = []
        for query in self.queries():
            output += query.columns(schema=schema)
        return list(set(output))
    
    def expandShortcuts(self, basetable=None):
        """
        Expands any shortcuts that were created for this query.  Shortcuts
        provide the user access to joined methods using the '.' accessor to
        access individual columns for referenced tables.
        
        :param      basetable | <orb.Table> || None
        
        :usage      |>>> from orb import Query as Q
                    |>>> # lookup the 'username' of foreign key 'user'
                    |>>> Q('user.username') == 'bob.smith'
        
        :return     <orb.Query> || <orb.QueryCompound>
        """
        output = self.copy()
        queries = []
        for query in output._queries:
            queries.append(query.expandShortcuts(basetable))
        output._queries = queries
        return output
    
    def findValue(self, column, instance=1):
        """
        Looks up the value for the inputed column name for the given instance.
        If the instance == 1, then this result will return the value and a
        0 instance count, otherwise it will decrement the instance for a
        matching column to indicate it was found, but not at the desired
        instance.
        
        :param      column   | <str>
                    instance | <int>
        
        :return     (<bool> success, <variant> value, <int> instance)
        """
        for query in self.queries():
            success, value, instance = query.findValue(column, instance)
            if success:
                return (success, value, 0)
        return (False, None, instance)
    
    def isNegated(self):
        """
        Returns whether or not this query is negated.
        
        :return <bool>
        """
        return self._negate
    
    def isNull(self):
        """
        Returns whether or not this join is empty or not.
        
        :return     <bool>
        """
        am_null = True
        for query in self._queries:
            if ( not query.isNull() ):
                am_null = False
                break
        
        return am_null
    
    def name(self):
        return self._name
    
    def negated(self):
        """
        Negates this instance and returns it.
        
        :return     self
        """
        qcompound = QueryCompound(*self._queries)
        qcompound._op     = self._op
        qcompound._negate = not self._negate
        return qcompound
    
    def operatorType(self):
        """
        Returns the operator type for this compound.
        
        :return     <QueryCompound.Op>
        """
        return self._op
    
    def or_(self, other):
        """
        Creates a new compound query using the 
        QueryCompound.Op.Or type.
        
        :param      other   <Query> || <QueryCompound>
        
        :return     <QueryCompound>
        
        :sa         or_
        
        :usage      |>>> from orb import Query as Q
                    |>>> query = (Q('test') != 1).or_(Q('name') == 'Eric')
                    |>>> print query
                    |(test isNot 1 or name is Eric)
        """
        if ( other is None or other.isNull() ):
            return self
            
        elif ( self.isNull() ):
            return other
        
        # grow this objects list if the operator types are the same
        if ( self.operatorType() == QueryCompound.Op.Or and
             not self.isNegated() ):
            queries = list(self._queries)
            queries.append(other)
            opts = { 'op': QueryCompound.Op.Or }
            
            # pylint: disable-msg=W0142
            return QueryCompound(*queries, **opts)
        
        return QueryCompound(self, other, op = QueryCompound.Op.Or)
    
    def queries(self):
        """
        Returns the list of queries that are associated with
        this compound.
        
        :return     <list> [ <Query> || <QueryCompound>, .. ]
        """
        return self._queries
    
    def removed(self, columnName):
        """
        Removes the query containing the inputed column name from this
        query set.
        
        :param      columnName | <str>
        
        :return     <QueryCompound>
        """
        out = self.copy()
        new_queries = []
        for query in out._queries:
            new_queries.append(query.removed(columnName))
        
        out._queries = new_queries
        return out
    
    def setName(self, name):
        self._name = str(name)
    
    def setOperatorType(self, op):
        """
        Sets the operator type that this compound that will be
        used when joining together its queries.
        
        :param      op      <QueryCompound.Op>
        """
        self._op = op
    
    def tables(self):
        """
        Returns the tables that this query is referencing.
        
        :return     [ <subclass of Table>, .. ]
        """
        output = []
        for query in self._queries:
            output += query.tables()
        
        return list(set(output))
    
    def toString(self):
        """
        Returns this query instance as a semi readable language
        query.
        
        :warning    This method will NOT return a valid SQL statement.  The
                    backend classes will determine how to convert the Query
                    instance to whatever lookup code they need it to be.
        
        :return     <str>
        """
        optypestr = QueryCompound.Op[self.operatorType()]
        op_type = ' %s ' % projex.text.underscore(optypestr)
        query = '(%s)' % op_type.join([q.toString() for q in self.queries()])
        if ( self.isNegated() ):
            query = 'NOT ' + query
        return query
    
    def toDict(self):
        """
        Creates a dictionary representation of this query.
        
        :return     <dict>
        """
        output = {}
        
        if self.isNull():
            return output
        
        output['type']    = 'compound'
        output['name']    = self.name()
        output['op']      = self.operatorType()
        output['negated'] = self.isNegated()
        
        queries = []
        for query in self.queries():
            queries.append(query.toDict())
        
        output['queries'] = queries
        return output
    
    def toXml(self, xparent=None):
        """
        Returns this query as an XML value.
        
        :param      xparent | <xml.etree.ElementTree.Element> || None
        
        :return     <xml.etree.ElementTree.Element>
        """
        if self.isNull():
            return None
        
        if xparent is None:
            xquery = ElementTree.Element('compound')
        else:
            xquery = ElementTree.SubElement(xparent, 'compound')
        
        xquery.set('name', str(self.name()))
        xquery.set('op', str(self.operatorType()))
        xquery.set('negated', str(self.isNegated()))
        
        for query in self.queries():
            query.toXml(xquery)
        
        return xquery
    
    def toXmlString(self, indented=False):
        """
        Returns this query as an XML string.
        
        :param      indented | <bool>
        
        :return     <str>
        """
        xml = self.toXml()
        if indented:
            projex.text.xmlindent(xml)
        
        return ElementTree.tostring(xml)
    
    def validate(self, record):
        """
        Validates the inputed record against this query compound.
        
        :param      record | <orb.Table>
        """
        op      = self._op
        queries = self.queries()
        
        if ( not queries ):
            return False
        
        for query in queries:
            valid = query.validate(record)
            
            if ( op == QueryCompound.Op.And and not valid ):
                return False
            elif ( op == QueryCompound.Op.Or and valid ):
                return True
        
        return op == QueryCompound.Op.And
    
    @staticmethod
    def build( compound, queries ):
        """
        Builds a compound based on the inputed compound string.  This should 
        look like: ((QUERY_1 and QUERY_2) or (QUERY_3 and QUERY_4)).  The 
        inputed query dictionary should correspond with the keys in the string.
        
        This method will be called as part of the Query.fromString method and 
        probably never really needs to be called otherwise.
        
        :param      compound | <str>
                    queries  | [<Query>, ..]
        
        :return     <Query> || <QueryCompound>
        """
        found      = False
        open       = 0
        indexStack = []
        compounds  = {}
        new_text   = projex.text.encoded(compound)
        
        for index, char in enumerate(projex.text.encoded(compound)):
            # open a new compound
            if ( char == '(' ):
                indexStack.append(index)
                
            # close a compound
            elif ( char == ')' and indexStack ):
                openIndex = indexStack.pop()
                match     = compound[openIndex+1:index]
                
                if ( not match ):
                    continue
                
                # create the new compound
                new_compound = QueryCompound.build(match, queries)
                
                key = 'QCOMPOUND_%i' % (len(compounds) + 1)
                compounds[key] = new_compound
                
                new_text = new_text.replace('(' + match + ')', key)
        
        new_text = new_text.strip('()')
        query    = Query()
        last_op  = 'and'
        for section in new_text.split():
            section = section.strip('()')
            
            # merge a compound
            if ( section in compounds ):
                section_q = compounds[section]
            
            elif ( section in queries ):
                section_q = queries[section]
            
            elif ( section in ('and', 'or') ):
                last_op = section
                continue
            
            else:
                logger.warning('Missing query section: %s', section)
                continue
            
            if ( query is None ):
                query = section_q
            elif ( last_op == 'and' ):
                query &= section_q
            else:
                query |= section_q
        
        return query
    
    @staticmethod
    def fromDict(data):
        if data.get('type') != 'compound':
            return Query.fromDict(data)
        
        compound = QueryCompound()
        compound.setName(data.get('name', ''))
        compound._negated = data.get('negated') == 'True'
        compound.setOperatorType(int(data.get('op', '1')))
        
        queries = []
        for subdata in data.get('queries', []):
            queries.append(Query.fromDict(subdata))
        
        compound._queries = queries
        return compound
    
    @staticmethod
    def fromString( querystr ):
        """
        Returns a new compound from the inputed query string.  This simply calls
        the Query.fromString method, as the two work the same.
        
        :param      querystr | <str>
        
        :return     <Query> || <QueryCompound> || None
        """
        return Query.fromString(querystr)
    
    @staticmethod
    def fromXml(xquery):
        if xquery.tag == 'query':
            return Query.fromXml(xquery)
        
        compound = QueryCompound()
        compound.setName(xquery.get('name', ''))
        compound._negated = xquery.get('negated') == 'True'
        compound.setOperatorType(int(xquery.get('op', '1')))
        
        queries = []
        for xsubquery in xquery:
            queries.append(Query.fromXml(xsubquery))
        
        compound._queries = queries
        return compound
    
    @staticmethod
    def fromXmlString(xquery_str):
        """
        Returns a query from the XML string.
        
        :param      xquery_str | <str>
        
        :return     <orb.Query> || <orb.QueryCompound>
        """
        try:
            xml = ElementTree.fromstring(xquery_str)
        except ExpatError:
            return Query()
        
        return Query.fromXml(xml)
    
    @staticmethod
    def typecheck(obj):
        """
        Returns whether or not the inputed object is a QueryCompound object.
        
        :param      obj     <variant>
        
        :return     ,bool>
        """
        return isinstance( obj, QueryCompound )