
def get_oid_from_relname(relname):
    statement = """SELECT c.oid, n.nspname, c.relname
    FROM pg_catalog.pg_class c
    LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
    WHERE pg_catalog.pg_table_is_visible(c.oid)
    AND c.relname ~ '^%s$' ORDER BY 2, 3""" % relname
    return statement

def get_oid_relinfo(oid):
    statement = """SELECT relhasindex, relkind, relchecks, reltriggers,
    relhasrules FROM pg_catalog.pg_class WHERE oid = '%s'""" % oid
    return statement

def get_attributes_for_oid(oid):
    statement = """SELECT a.attname,
    pg_catalog.format_type(a.atttypid, a.atttypmod),
    (SELECT substring(d.adsrc for 128) FROM pg_catalog.pg_attrdef d
    WHERE d.adrelid = a.attrelid AND d.adnum = a.attnum AND a.atthasdef),
    a.attnotnull, a.attnum
    FROM pg_catalog.pg_attribute a
    WHERE a.attrelid = '%s' AND a.attnum > 0 AND NOT a.attisdropped
    ORDER BY a.attnum""" % oid
    return statement

def get_key_info_for_oid(oid):
    statement = """SELECT c2.relname, i.indisprimary,
    i.indisunique, pg_catalog.pg_get_indexdef(i.indexrelid)
    FROM pg_catalog.pg_class c, pg_catalog.pg_class c2, pg_catalog.pg_index i
    WHERE c.oid = '%s' AND c.oid = i.indrelid AND i.indexrelid = c2.oid
    ORDER BY i.indisprimary DESC, i.indisunique DESC, c2.relname""" % oid
    return statement

def get_trigger_info_for_oid(oid):
    statement = """SELECT t.tgname, pg_catalog.pg_get_triggerdef(t.oid)
    FROM pg_catalog.pg_trigger t
    WHERE t.tgrelid = '%s'
    AND (not tgisconstraint
    OR NOT EXISTS
    (SELECT 1 FROM pg_catalog.pg_depend d
    JOIN pg_catalog.pg_constraint c ON
    (d.refclassid = c.tableoid AND d.refobjid = c.oid)
    WHERE d.classid = t.tableoid AND d.objid = t.oid
    AND d.deptype = 'i' AND c.contype = 'f'))""" % oid
    return statement

def get_constraints_for_oid(oid):
    statement = """SELECT conname,
    pg_catalog.pg_get_constraintdef(oid) as condef
    FROM pg_catalog.pg_constraint r
    WHERE r.conrelid = '%s' AND r.contype = 'f'""" % oid
    return statement

def get_parent_relations_for_oid(oid):
    statement = """SELECT c.relname FROM
    pg_catalog.pg_class c, pg_catalog.pg_inherits i
    WHERE c.oid=i.inhparent AND i.inhrelid = '%s'
    ORDER BY inhseqno ASC""" % oid
    return statement

def get_relations_dt():
    statement = """SELECT n.nspname as "Schema",
    c.relname as "Name",
    CASE c.relkind WHEN 'r' THEN 'table' WHEN 'v' THEN 'view' WHEN 'i' THEN 'index' WHEN 'S' THEN 'sequence' WHEN 's' THEN 'special' END as "Type",
    u.usename as "Owner"
    FROM pg_catalog.pg_class c
    LEFT JOIN pg_catalog.pg_user u ON u.usesysid = c.relowner
    LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
    WHERE c.relkind IN ('r','')
    AND n.nspname NOT IN ('pg_catalog', 'pg_toast')
    AND pg_catalog.pg_table_is_visible(c.oid)
    ORDER BY 1,2"""
    return statement

def get_oid(cursor, table):
    cursor.execute(get_oid_from_relname(table))
    return cursor.fetchall()[0].oid
    

def get_attributes(cursor, table):
    oid = get_oid(cursor, table)
    cursor.execute(get_attributes_for_oid(oid))
    return cursor.fetchall()

def get_pkey_info(cursor, table):
    oid = get_oid(cursor, table)
    cursor.execute(get_key_info_for_oid(oid))
    return cursor.fetchall()

def get_constraints(cursor, table):
    oid = get_oid(cursor, table)
    cursor.execute(get_constraints_for_oid(oid))
    return cursor.fetchall()


def get_relations(cursor):
    cursor.execute(get_relations_dt())
    return cursor.fetchall()


if __name__ == '__main__':
    from paella.profile.base import PaellaConnection
    from paella.db.midlevel import StatementCursor
    conn = PaellaConnection()
    s = StatementCursor(conn)

    def get_tables():
        s.execute(get_relations_dt())
        return s.fetchall()
