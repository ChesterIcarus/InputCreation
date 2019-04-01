from typing import Dict, Tuple, List, T
import MySQLdb as sql
import MySQLdb.connections as connections
from warnings import warn


class DatabaseHandle:
    connection = connections.Connection
    cursor = connections.cursors.Cursor
    user = None
    host = None
    db = None
    schema = None
    table = None

    def __init__(self, params: Dict[str, str] = None, handle=None):
        if type(handle) is DatabaseHandle:
            self = handle

        if isinstance(params, dict):
            try:
                self.connection = sql.connect(user=params['user'],
                                              password=params['password'],
                                              db=params['db'], host=params['host'])
                self.cursor = self.connection.cursor()
                self.user = params['user']
                self.host = params['host']
                self.db = params['db']
            except sql._exceptions.DatabaseError:
                # Creating the database that didn't exist, if that was the error above
                connection: sql.connections.Connection
                connection = sql.connect(user=params['user'],
                                         password=params['password'],
                                         db='mysql', host=params['host'])
                cursor = connection.cursor()
                cursor.execute(f'CREATE DATABASE {params["db"]}')
                cursor.commit()
                cursor.close()
                connection.close()
                self.connection = sql.connect(user=params['user'],
                                              password=params['password'],
                                              db=params['db'], host=params['host'])
                self.cursor = self.connection.cursor()
                self.user = params['user']
                self.host = params['host']
                self.db = params['db']

        else:
            self.user = None
            self.host = None
            self.db = None
            self.cursor = None
            self.connection = None
            warn('No valid database passed, DatabaseHandle initialized without connection')
        if 'table' in params:
            self.table = params['table']
        else:
            self.table = None
        if 'schema' in params:
            self.schema = params['schema']
            self.columns = [column.split(' ')[0]
                            for column in params['schema']]
        else:
            self.columns = None

    def create_table(self, table=None, schema=None):
        if table is not None:
            self.table = table
        if schema is not None:
            self.columns = [column.split(' ')[0] for column in schema]
            self.schema = schema
        sql_schema = f"({(', ').join(self.schema)})"
        exec_str = f''' DROP TABLE IF EXISTS 
                            {self.db}.{self.table}'''
        self.cursor.execute(exec_str)
        self.connection.commit()
        exec_str = f''' CREATE TABLE 
                            {self.db}.{self.table} 
                        {sql_schema}'''
        self.cursor.execute(exec_str)
        self.connection.commit()

    def create_index(self, index_name, index_columns):
        formed_index_cols = (', ').join(index_columns)
        exec_str = f'''CREATE INDEX 
                            {index_name}
                        ON {self.db}.{self.table}
                            ({formed_index_cols})'''
        self.cursor.execute(exec_str)
        self.connection.commit()

    def alter_add_composite_key(self, fields):
        formed_index_cols = (', ').join(fields)
        exec_str = f'''ALTER TABLE {self.db}.{self.table}
                        ADD PRIMARY KEY ({formed_index_cols})'''
        self.cursor.execute(exec_str)
        self.connection.commit()

    def write_rows(self, data):
        s_strs = f"({(', ').join(['%s'] * len(self.columns))})"

        exec_str = f''' INSERT INTO {self.db}.{self.table} 
                        VALUES {s_strs} '''
        self.cursor.executemany(exec_str, data)
        self.connection.commit()
