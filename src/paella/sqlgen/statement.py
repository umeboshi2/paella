from write import delete, update, insert
from select import simple_select, complex_select
from clause import SimpleClause, In, NotIn

write_types = ['delete', 'update', 'insert']

all_types = write_types


class Statement(object):
    def __init__(self, type='select', table=None,
                 data=None, clause=None):
        object.__init__(self)
        self.table = table
        self.type = type
        self.data = data
        self.clause = clause
        self.fields = ['*']
        
    def _create_statement(self):
        if self.type == 'delete':
            return self.delete()
        elif self.type == 'insert':
            return self.insert()
        elif self.type == 'update':
            return self.update()
        else:
            return self.select()

    def delete(self, table=None, clause=None):
        if not table:
            table = self.table
        if not clause:
            clause = self.clause
        return delete(table, clause=clause)

    def insert(self, table=None, data=None):
        if not table:
            table = self.table
        if not data:
            data = self.data
        return insert(table, data)

    def update(self, table=None, data=None, clause=None):
        if not table:
            table = self.table
        if not data:
            data = self.data
        if not clause:
            clause = self.clause
        return update(table, data, clause=clause)

    def select(self, fields=None, table=None, clause=None,
               group=None, having=None, order=None):
        if not fields:
            fields = self.fields
        if not table:
            table = self.table
        if not clause:
            clause = self.clause
        return complex_select(table, fields, clause, group,
                              having, order)
    
    def set(self, data):
        self.data = data

    def set_clause(self, items, cmp='=', join='and'):
        self.clause = SimpleClause(items, cmp=cmp, join=join)
        
    def clear(self, table=None, data=None, clause=None):
        if table:
            self.table = None
        if data:
            self.data = None
        if clause:
            self.clause = None
        if not table and not data and not clause:
            print 'all cleared'
            self.table = None
            self.data = None
            self.clause = None
            

    def __repr__(self):
        return self._create_statement()


if __name__ == '__main__':
    items = [('foo', 'bar'), ('fu', 'bar'), ('fi', 'bar')]
    c = SimpleClause(items)
    d = SimpleClause([items[1]])
    s = Statement('insert', 'footable', {'ab':'cd', 'ef':'gh'}, c)
