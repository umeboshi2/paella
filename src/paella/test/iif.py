import csv
    
from paella.sqlgen.defaults import BignameTable
from paella.sqlgen.write import insert

def iif_to_list(fd):
    parser = csv.parser(field_sep='\t')
    rows = []
    while 1:
        line = ifile.readline()
        if not line:
            break
        fields = parser.parse(line)
        if not fields:
            continue
        rows.append(fields)
    fd.close()
    return rows

def is_header(row):
    return row[0][0] == '!'

def get_head(row):
    return row[0][1:]

def split_list(ilist):
    ndict = {}
    fdict = {}
    for row in ilist:
        if is_header(row):
            if 'DESC' in row:
                row[row.index('DESC')] = '_DESC'
            if 'QNTY' in row:
                row[row.index('QNTY')] = '_QNTY'
            if 'LIMIT' in row:
                row[row.index('LIMIT')] = '_LIMIT'
            if '1099' in row:
                row[row.index('1099')] = '_1099'
            if 'AMOUNT' in row:
                row[row.index('AMOUNT')] = '_AMOUNT'
            key = get_head(row)
            if key in ndict:
                print 'key %s already in ndict' %key
            else:
                ndict[key] = []
                fdict[key] = row
        else:
            key = row[0]
            if key not in ndict:
                print 'header not made for %s'  %key
            else:
                ndict[key].append(row)
    return fdict, ndict

def make_tables(field_dict):
    table_dict = {}
    for tname in field_dict:
        rows = field_dict[tname][1:]
        if len(rows):
            table_dict[tname] = BignameTable(tname, rows)
    return table_dict

def fill_table(cursor, table, rows):
    columns = [x.name for x in table.columns]
    for row in rows:
        idict = dict(zip(columns, row[1:]))
        cursor.execute(insert(table.name, idict))
        #print insert(table.name, idict)
        
def fill_tables(cursor, table_dict, data_dict):
    for table in table_dict.values():
        rows = data_dict[table.name]
        if len(rows):
            cursor.execute('create table %s' %table)
            #print 'create table %s' %table
            fill_table(cursor, table, rows)
        

if __name__ == '__main__':
    from paella.db.lowlevel import QuickConn
    import sys
    ifile = file(sys.argv[1])
    r = iif_to_list(ifile)
    f, d = split_list(r)
    td = make_tables(f)
    c = QuickConn()
    cmd = CommandCursor(c, 'dsfsdf')
    def dtables():
        for t in cmd.tables():
            if t != 'footable':
                cmd.execute('drop table %s' %t)
    
