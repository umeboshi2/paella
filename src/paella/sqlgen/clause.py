from operator import and_, or_
from pyPgSQL.libpq import PgQuoteString as quote
from classes import cj_fields


cond_op = ['=', '<', '>', '<=', '>=', '<>']


def paren(expr):
    return '(%s)' %expr

class Condition(object):
    def __init__(self):
        object.__init__(self)
        

class CondOp(object):
    def __init__(self, left, right, op, quoted=True):
        object.__init__(self)
        self.left = left
        self.right = right
        self.op = op
        self._quote = quoted
        if type(self.right) in [int, long, bool]:
            self._quote = False
            
    def __repr__(self):
        if self._quote:
            expr =  ' '.join(map(str, [self.left, self.op, quote(str(self.right))]))
        else:
            expr = ' '.join(map(str, [self.left, self.op, self.right]))
        return '%s' %expr

    def __str__(self):
        return self.__repr__()
        
    def __and__(self, other):
        left, right = map(paren, map(str, [self, other]))
        return CondOp(left, right, 'and', quoted=False)

    def __or__(self, other):
        left, right = map(paren, map(str, [self, other]))
        return CondOp(left, right, 'or', quoted=False)

class Eq(CondOp):
    def __init__(self, left, right):
        CondOp.__init__(self, left, right, '=')

class Neq(CondOp):
    def __init__(self, left, right):
        CondOp.__init__(self, left, right, '!=')

class Gt(CondOp):
    def __init__(self, left, right):
        CondOp.__init__(self, left, right, '>')

class Lt(CondOp):
    def __init__(self, left, right):
        CondOp.__init__(self, left, right, '<')

class Gte(CondOp):
    def __init__(self, left, right):
        CondOp.__init__(self, left, right, '>=')

class Lte(CondOp):
    def __init__(self, left, right):
        CondOp.__init__(self, left, right, '<=')


    

class Like(CondOp):
    def __init__(self, left, right):
        CondOp.__init__(self, left, right, 'like')

class _In(CondOp):
    def __init__(self, left, right, quoted=False, op='in'):
        if type(right) is str:
            right_expr = paren(right)
        else:
            joined = ', '.join(map(quote, map(str, right)))
            right_expr = paren(joined)
        CondOp.__init__(self, left, right_expr, op, quoted=quoted)

class In(_In):
    def __init__(self, left, right, quoted=False):
        _In.__init__(self, left, right, quoted=quoted, op='in')



class NotIn(_In):
    def __init__(self, left, right, quoted=False):
        _In.__init__(self, left, right, quoted=quoted, op='not in')


class SimpleClause(object):
    def __init__(self, items=None, cmp='=', join='and'):
        object.__init__(self)
        self.items = [CondOp(left, right, op=cmp) for left, right in items]
        self.cmp = cmp
        if join == 'and':
            self.join = and_
        elif join == 'or':
            self.join = or_

    def __repr__(self):
        return str(reduce(self.join, self.items))

def one_many(onefield, onevalue, manyfield, manyvalues, cmp='and'):
    if cmp == 'and':
        return Eq(onefield, onevalue) & In(manyfield, manyvalues)
    elif cmp == 'or':
        return Eq(onefield, onevalue) | In(manyfield, manyvalues)
                                         


if __name__ == '__main__':
    co = CondOp('foo', 'bar')
    
    a = CondOp('foo', 'bar')
    b = CondOp('id', 23)
    c = In('a', ['a', 'b', 'c', 'd', 'e'])
    items = [('foo', 'bar'), ('fu', 'bar'), ('fi', 'bar')]
    s = SimpleClause(items)
