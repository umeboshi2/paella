
def header(name, params, returns):
    lines = []
    lines.append('create or replace function %s(%s)' % (name, ','.join(params)))
    lines.append("returns %s as '" % returns)
    return lines

def pgsql_delete(name, tables, key):
    lines = header(name, ['varchar'], 'integer')
    lines.append('begin')
    for table in tables:
        line = "delete from %s where %s = $1 ;" % (table, key)
        lines.append(line)
    lines.append('return 0 ;')
    lines.append('end ;')
    lines.append("' language 'plpgsql';")
    return '\n'.join(lines) + '\n'

def branchlevels(name, table, column, parent='parent'):
    lines = header(name, 'integer', 'integer')
    baseclause = '%s = $1' % parent
    bselect = 'select %s from %s where %s' % (column, table, baseclause)
    mselect = 'select %s from %s where %s in' % (column, table, parent)
    cselect = 'select into count count(%s) from %s where %s in' % \
              (column, table, parent)
    lines.append('declare')
    lines.append('total := 0;')
    lines.append('count := 1;')
    lines.append('begin')
    lines.append('while count > 0 loop')
    
    
    
