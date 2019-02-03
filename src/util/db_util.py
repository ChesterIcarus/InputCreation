import MySQLdb as sql
import MySQLdb.connections as connections

from getpass import getpass


class DatabaseHandle:
    connection = connections.Connection
    cursor = connections.cursors.Cursor
    user = None
    host = None
    db = None
    schema = None
    table = None

    def __init__(self, user, password, db, host):
        self.connection = sql.connect(
            user=user, password=password, host=host)
        self.cursor = self.connection.cursor()
        self.user = user
        self.host = host
        self.db = db
        self.schema = None
        self.table = None

    def create_db(self, table, schema):
        self.cursor.execute(f'DROP DATABASE IF EXISTS {self.db}')
        self.connection.commit()
        self.cursor.execute(f'CREATE DATABASE {self.db}')
        self.connection.commit()
        self.cursor.execute(f'CREATE TABLE {self.db}.{table} {schema}')
        self.connection.commit()
        self.schema = schema
        self.table = table

    def write_rows(self, data):
        exec_str = f'''
                INSERT INTO {self.db}.{self.table} 
                    VALUES 
                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    '''
        self.cursor.executemany(exec_str, data)
        self.connection.commit()
