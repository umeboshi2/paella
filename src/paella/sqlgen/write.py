from pyPgSQL.libpq import PgQuoteString as quote
from classes import cj_fields


def _set_eq_(key, value):
    return "%s = %s" %(key, quote(str(value)))
def _set_vals_(a_dict):
    return cj_fields([_set_eq_(k,v) for k,v in a_dict.items()])

#make string key1="val",key2="val"  ...
def set_values(adict):
    return _set_vals_(adict)

#return a string tuple from list
def make_tuple(alist):
    return '(%s)' % cj_fields(alist)

#return a list of 2 tuples [key tup, val tup]
#where val tup is quoted
def tuplize_dict(adict):
    klist, vlist = [], []
    for k,v in adict.items():
        klist.append(k)
        if type(v) in [int, long]:
            vlist.append(str(v))
        elif v is None:
            vlist.append('NULL')
        else:
            vlist.append(quote(str(v)))
    return tuple(map(make_tuple, [klist, vlist]))

##########
#Statements
##########

def delete(table, clause=None):
    query = 'delete from %s' % table
    if clause:
        query += ' where %s' % clause
    return query

def update(table, adict, clause=None):
    vals = set_values(adict)
    query = 'update %s set %s' %(table, vals)
    if clause:
        query += ' where %s' % clause
    return query

#insert into table (keys) values (values) from adict
def insert(table, adict):
    if type(adict) in [list, tuple]:
        vals = make_tuple(map(quote, map(str, adict)))
        query = 'insert into %s values %s' \
               %(table, vals)
    else:
        fields, vals = tuplize_dict(adict)
        query =  'insert into %s %s values %s' \
               %(table, fields, vals)
    #print query
    return query

if __name__ == '__main__':
    print insert('footable', {'b' : 'c', 'x' : 'y'})
    
