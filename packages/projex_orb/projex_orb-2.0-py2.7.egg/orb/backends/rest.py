#!/usr/bin/python

""" Defines the backend connection class for JSON/REST remote API's. """

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
__depends__        = ['']
__version_info__   = (0, 0, 0)
__version__        = '%i.%i.%i' % __version_info__


import datetime
import logging
from xml.etree import ElementTree
try:
    import requests
except ImportError:
    requests = None

import projex.errors
import projex.text
import projex.rest

from orb                 import errors, settings, Orb
from orb.common          import ColumnType
from orb.connection      import Connection, DatabaseOptions, LookupOptions
from orb.transaction     import Transaction
from orb.table           import Table
from orb.join            import Join
from orb.query           import Query as Q, QueryCompound
from orb.recordset       import RecordSet
from orb.valuemapper     import ValueMapper

logger = logging.getLogger(__name__)

# assign record encode/decoders
def record_encoder(py_obj):
    # encode a record
    if Table.recordcheck(py_obj):
        return (True, py_obj.primaryKey())
    # encode a recordset
    elif RecordSet.typecheck(py_obj):
        return (True, py_obj.primaryKeys())
    # encode a query
    elif Q.typecheck(py_obj) or QueryCompound.typecheck(py_obj):
        return (True, py_obj.toDict())
    return (False, None)

projex.rest.register(record_encoder)

#------------------------------------------------------------------------------

class REST(Connection):
    def __init__(self, database):
        super(REST, self).__init__(database)
        
        self.setThreadEnabled(True)
    
    def close(self):
        """
        Closes the connection to the datbaase for this connection.
        
        :return     <bool> closed
        """
        return True
    
    def commit(self):
        """
        Commits the changes to the current database connection.
        
        :return     <bool> success
        """
        return True
    
    def count( self, table_or_join, lookup, options ):
        """
        Returns the number of records that exist for this connection for
        a given lookup and options.
        
        :sa         distinct, select
        
        :param      table_or_join | <orb.Table> || <orb.Join>
                    lookup        | <orb.LookupOptions>
                    options       | <orb.DatabaseOptions>
        
        :return     <int>
        """
        # ensure we're working with a valid table
        if not Table.typecheck(table_or_join):
            logger.debug('REST backend only supports table lookups.')
            return {}
        
        # create the query data
        py_data = {'table': table_or_join.schema().name(),
                   'lookup': lookup.toDict(),
                   'options': options.toDict()}
        
        response = self.execute('count', py_data)
        return int(response.get('count', 0))
    
    def distinct(self, table_or_join, lookup, options):
        """
        Returns the distinct set of records that exist for a given lookup
        for the inputed table or join instance.
        
        :sa         count, select
        
        :param      table_or_join | <orb.Table> || <orb.Join>
                    lookup        | <orb.LookupOptions>
                    options       | <orb.DatabaseOptions>
        
        :return     {<str> columnName: <list> value, ..}
        """
        # ensure we're working with a valid table
        if not Table.typecheck(table_or_join):
            logger.debug('REST backend only supports table lookups.')
            return {}
        
        # create the query data
        py_data = {'table': table_or_join.schema().name(),
                   'lookup': lookup.toDict(),
                   'options': options.toDict()}
        
        response = self.execute('distinct', py_data)
        if not 'records' in response:
            raise errors.InvalidResponse('distinct', response)
        
        records = response['records']
        if type(records) == list:
            return {lookup.columns[0]: records}
        else:
            return records
    
    def execute(self, command, data=None, flags=None):
        """
        Executes the inputed command into the current 
        connection cursor.
        
        :param      command  | <str>
                    data     | <dict> || None
                    flags    | <orb.DatabaseFlags>
        
        :return     <variant> returns a native set of information
        """
        # ensure we have a database
        db = self.database()
        if not db:
            raise errors.DatabaseNotFoundError()
        
        # generate the rest API url
        url = db.host().rstrip('/') + '/' + command
        
        # convert the data to json format
        json_data = projex.rest.jsonify(data)
        try:
            response = requests.post(url,
                                     json_data,
                                     auth=(db.username(), db.password()))
        except Exception, err:
            logger.debug('Error processing request.\n%s', err)
            response = None
        
        # process the response information
        if response and response.status_code == 200:
            return projex.rest.unjsonify(response.content)
        else:
            return {}
    
    def insert(self, records, lookup, options):
        """
        Inserts the database record into the database with the
        given values.
        
        :param      record      | <orb.Table>
                    options     | <orb.DatabaseOptions>
        
        :return     <bool>
        """
        # convert the recordset to a list
        if RecordSet.typecheck(records):
            records = list(records)
        
        # wrap the record in a list
        elif Table.recordcheck(records):
            records = [records]
        
        submit = []
        submit_records = []
        changeset = []
        for record in records:
            changes = record.changeset(columns=lookup.columns)
            if not changes:
                continue
            
            changeset.append(changes)
            table = record.schema().name()
            
            values = dict([(x, y[1]) for x, y in changes.items()])
            values = self.processValue(values)
            
            submit_records.append(record)
            submit.append({'table': table,
                           'id': record.primaryKey(),
                           'values': values})
        
        # create the query data
        if not submit:
            return {}
        
        py_data = {'records': submit}
        response = self.execute('insert', py_data)
        
        if 'error' in response:
            raise errors.InvalidResponse('insert', response['error'])
        
        # update the records
        ids = response.get('ids')
        if not (ids and len(ids) == len(submit_records)):
            raise errors.InvalidResponse('insert', 
                                         'No IDs were returned from insert.')
        else:
            for i, record in enumerate(submit_records):
                record._updateFromDatabase({'PRIMARY_KEY': ids[i]})
                record._markAsLoaded(self.database(), columns=lookup.columns)
        
        if len(changeset) == 1:
            return changeset[0]
        return changeset
    
    def isConnected(self):
        """
        Returns whether or not this conection is currently
        active.
        
        :return     <bool> connected
        """
        return True
    
    def removeRecords( self, schema, primaryKeys, options ):
        """
        Removes the given records from the inputed schema.  This method is 
        called from the <Connection.remove> method that handles the pre
        processing of grouping records together by schema and only works
        on the primary key.
        
        :param      schema      | <orb.TableSchema>
                    primaryKeys | [<variant> pkey, ..]
                    options     | <orb.DatabaseOptions>
        
        :return     <int> | number of rows removed
        """
        py_data = {'table': schema.name(),
                   'ids': primaryKeys,
                   'options': options.toDict()}
        
        response = self.execute('remove', py_data)
        return response.get('removed', 0)
    
    def select(self, table_or_join, lookup, options):
        """
        Selects the records from the database for the inputed table or join
        instance based on the given lookup and options.
                    
        :param      table_or_join   | <subclass of orb.Table>
                    lookup          | <orb.LookupOptions>
                    options         | <orb.DatabaseOptions>
        
        :return     [<variant> result, ..]
        """
        if not lookup.order and Table.typecheck(table_or_join):
            lookup.order = table_or_join.schema().defaultOrder()
        
        # ensure we're working with a valid table
        if not Table.typecheck(table_or_join):
            logger.debug('REST backend only supports table lookups.')
            return {}
        
        # create the query data
        py_data = {'table': table_or_join.schema().name(),
                   'lookup': lookup.toDict(),
                   'options': options.toDict()}
        
        response = self.execute('select', py_data)
        if 'error' in response:
            raise errors.InvalidResponse('select', response['error'])
        
        elif not 'records' in response:
            raise errors.InvalidResponse('select', response)
        
        records = response['records']
        return records
    
    def open(self):
        """
        Opens a new database connection to the datbase defined
        by the inputed database.
        
        :return     <bool> success
        """
        return True
    
    def rollback(self):
        """
        Rollsback the latest code run on the database.
        """
        return False
    
    def update(self, records, lookup, options):
        """
        Updates the database record into the database with the
        given values.
        
        :param      record  | <orb.Table>
                    options | <orb.DatabaseOptions>
        
        :return     <bool>
        """
        # convert the recordset to a list
        if RecordSet.typecheck(records):
            records = list(records)
        
        # wrap the record in a list
        elif Table.recordcheck(records):
            records = [records]
        
        submit_records = []
        submit = []
        changeset = []
        for record in records:
            changes = record.changeset(columns=lookup.columns)
            if not changes:
                continue
            
            changeset.append(changes)
            
            table = record.schema().name()
            
            values = dict([(x, y[1]) for x, y in changes.items()])
            values = self.processValue(values)
            
            submit_records.append(record)
            submit.append({'table': table,
                           'id': record.primaryKey(),
                           'values': values})
        
        # create the query data
        if not submit:
            return {}
        
        py_data = {'records': submit}
        response = self.execute('update', py_data)
        
        if 'error' in response:
            raise errors.InvalidResponse('update', response['error'])
        else:
            for i, record in enumerate(submit_records):
                record._markAsLoaded(self.database(), columns=lookup.columns)
        
        if len(changeset) == 1:
            return changeset[0]
        return changeset
    
    @staticmethod
    def processValue(value):
        if Table.recordcheck(value):
            return value.primaryKey()
        elif type(value) == dict:
            out = {}
            for key, val in value.items():
                out[key] = REST.processValue(val)
            return out
        elif type(value) in (list, tuple):
            typ = type(value)
            out = []
            for val in value:
                out.append(REST.processValue(val))
            return typ(out)
        else:
            return value
    
    @staticmethod
    def serve(method,
              json_data,
              database=None,
              username=None,
              password=None):
        """
        Processes the method from the network.  This method should be used on
        the server side to process client requests that are being generated
        using this REST backend.  You will need to call it from your web
        server passing along the requested data, and will generate a response
        in a JSON formated dictionary to be passed back.
        
        :param      method | <str>
                    json_data | <str>
        
        :return     <dict> | json_reponse
        """
        from orb import LookupOptions, DatabaseOptions, Orb
        
        # processing the inputed json information
        py_data  = projex.rest.unjsonify(json_data)
        database = py_data.get('database', database)
        table    = None
        record   = None
        lookup   = None
        options  = None
        values   = None
        ids      = None
        records  = None
        response = {}
        
        # extract the table from the call
        table = None
        if 'table' in py_data:
            table = Orb.instance().model(py_data['table'], database=database)
            if not table:
                return {'error': 'No %s table found.' % py_data['table']}
        
        # extract lookup information from the call
        if 'lookup' in py_data:
            lookup = LookupOptions.fromDict(py_data['lookup'])
        
        # extract option information from the call
        if 'options' in py_data:
            options = DatabaseOptions.fromDict(py_data['options'])
        
        # extract id information
        if 'ids' in py_data:
            ids = py_data['ids']
        
        # extract the record id information
        if 'record' in py_data:
            if not table:
                return {'error': 'No %s table found for record.'}
            
            record = table(py_data['record'])
        
        # extract records information
        elif 'records' in py_data:
            records = []
            for submit in py_data['records']:
                table = Orb.instance().model(submit['table'], database=database)
                if not table:
                    continue
                
                record = table(submit['id'])
                values = submit['values']
                record._Table__record_values.update(values)
                records.append(record)
        
        # extract value information from the call
        if 'values' in py_data:
            values = py_data.get('values')
            if record:
                record._Table__record_values.update(values)
        
        #----------------------------------------------------------------------
        # process methods
        #----------------------------------------------------------------------
        
        # get a count from the system
        if method == 'count':
            response = {'count': len(table.select(lookup, options))}
        
        # perform a distinct select
        elif method == 'distinct':
            options.inflateRecords = False
            rset = table.select(lookup, options)
            records = rset.distinct(lookup.columns)
            response = {'records': records}
        
        # insert a record into the database
        elif method == 'insert':
            rset = RecordSet(records)
            try:
                rset.commit()
                response['ids'] = rset.primaryKeys()
            except StandardError, err:
                response['error'] = str(err)
        
        # remove records from the database
        elif method == 'remove':
            if ids is None:
                response = {'error': 'No ids were supplied for removal'}
            else:
                count = table.select(where=Q(table).in_(ids)).remove()
                response = {'removed': count}
        
        # perform a select
        elif method == 'select':
            rset = table.select(lookup=lookup, options=options)
            response = {'records': rset.all(inflated=False, ignoreColumns=True)}
        
        # perform an update
        elif method == 'update':
            rset = RecordSet(records)
            try:
                rset.commit()
            except StandardError, err:
                response['error'] = str(err)
        
        # lookup not found
        else:
            response = {'error': '%s is an invalid rest call'}
        
        return projex.rest.jsonify(response)
    
if requests:
    Connection.register('REST', REST)