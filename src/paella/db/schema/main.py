from useless.sqlgen.admin import grant_public

from paella_tables import primary_sequences
from paella_tables import primary_tables
from paella_tables import SCRIPTS, MTSCRIPTS

from pgsql_functions import create_pgsql_functions


def insert_list(cursor, table, field, list):
    for value in list:
        cursor.insert(table=table, data={field : value})

def start_schema(conn):
    cursor = conn.cursor(statement=True)
    map(cursor.create_sequence, primary_sequences())
    tables, mapping = primary_tables()
    map(cursor.create_table, tables)
    insert_list(cursor, 'scriptnames', 'script', SCRIPTS)
    newscripts = [s for s in MTSCRIPTS if s not in SCRIPTS]
    insert_list(cursor, 'scriptnames', 'script', newscripts)
    cursor.execute(grant_public([x.name for x in tables]))
    cursor.execute(grant_public(['current_environment'], 'ALL'))
    cursor.execute(grant_public(['partition_workspace'], 'ALL'))
    create_pgsql_functions(cursor)
    
