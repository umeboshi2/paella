from useless.sqlgen.admin import grant_public, grant_user

from tables import primary_sequences
from tables import primary_tables
from tables import SCRIPTS, MTSCRIPTS

from pgsql_functions import create_pgsql_functions

class SchemaError(RuntimeError):
    pass

class AlreadyPresentError(RuntimeError):
    pass

def insert_list(cursor, table, field, list):
    for value in list:
        cursor.insert(table=table, data={field : value})

def start_schema(conn, installuser='paella'):
    cursor = conn.cursor(statement=True)
    tables, mapping = primary_tables()
    current_tables = cursor.tables()
    primary_table_names = [t.name for t in tables]
    startup = True
    for tname in primary_table_names:
        if tname in current_tables:
            startup = False
    if startup:
        map(cursor.create_sequence, primary_sequences())
        map(cursor.create_table, tables)
        insert_list(cursor, 'scriptnames', 'script', SCRIPTS)
        newscripts = [s for s in MTSCRIPTS if s not in SCRIPTS]
        insert_list(cursor, 'scriptnames', 'script', newscripts)
        paella_select = grant_user('SELECT', [x.name for x in tables], installuser)
        paella_full = grant_user('ALL',
                                 ['current_environment', 'partition_workspace'],
                                 installuser)
        paella_insert = grant_user('INSERT', ['default_environment'],
                                   installuser)
        for grant in paella_select, paella_full, paella_insert:
            cursor.execute(grant)
        #cursor.execute(grant_public([x.name for x in tables]))
        #cursor.execute(grant_public(['current_environment'], 'ALL'))
        #cursor.execute(grant_public(['partition_workspace'], 'ALL'))
        #cursor.execute(grant_user(['default_environment'], 'INSERT', 'paella')
        create_pgsql_functions(cursor)
    else:
        all_there = True
        for table in primary_table_names:
            if table not in current_tables:
                all_there = False
        # the AlreadyPresentError is a convenience error
        # it doesn't mean the schema is a-ok
        if all_there:
            raise AlreadyPresentError, 'it seems everything is already here'
        else:
            raise SchemaError, 'some primary tables already exist in the database'

    
