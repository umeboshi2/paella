from pyPgSQL.libpq import PgQuoteString as quote
from classes import cj_fields

cond_ops = ['=', '<', '>', '<=', '>=', '<>', 'like']
log_ops = ['and', 'or', 'not']


def _cond_expr(item, operator):
    return '%s %s %s' %(item[0], operator, quote(str(item[1])))

def _cond_expr2(item, operator):
    if not hasattr(item, 'item'):
        return '%s %s %s' %(item[0], operator, item[1])
    else:
        return '%s %s' %(operator, _cond_expr(item.item, item.operator))
def _log_expr(item, operator):
    if not hasattr(item, 'item'):
        return '%s %s'


class _Clause(object):
    def __init__(self, item, operator):
        object.__init__(self)
        self.item = item
        self.operator = operator

    def __repr__(self):
        return _cond_expr(self.item, self.operator)
    

class SimpleClause(object):
    def __init__(self, items=None,
                 cmp='=', join='and'):
        object.__init__(self)
        self.items = items
        self.cmp = cmp
        self.join = join

    def __write_clause__(self):
        subs = [_cond_expr(i, self.cmp) for i in self.items]
        jstring = ' %s ' % self.join
        return jstring.join(subs)

    def __repr__(self):
        return self.__write_clause__()
    
    


                
class Name(object):
    def __init__(self, name, alias=None):
        self.name =str(name)
        self.alias = alias

    def __repr__(self):
        if self.alias:
            return '%s as %s' %(self.name, self.alias)
        else:
            return self.name

class Join(object):
    def __init__(self, type, outer=None):
        self.type = type
        self.outer = outer


def simple_select(table, columns=None, clause=None):
    if columns is not None:
        if type(columns) != str:
            cols = cj_fields(list(columns))
        else:
            cols = columns
    else:
        cols = '*'
    sel = 'select %s from %s' %(cols, table)
    if clause:
        sel += ' where %s' % clause
    return sel

def complex_select(table, columns=None, clause=None,
                   group=None, having=None, order=None):
    sel = simple_select(table, columns=columns, clause=clause)
    if group:
        sel += ' GROUP BY %s' % cj_fields(group)
    if having:
        sel += ' HAVING %s' % having
    if order:
        sel += ' ORDER BY %s' % cj_fields(order)
    return sel

if __name__ == '__main__':
    items = [('foo', 'bar'), ('fu', 'bar'), ('fi', 'bar')]
    c = SimpleClause(items)
    d = SimpleClause([items[1]])
    
