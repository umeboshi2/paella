from sets import Set
from operator import and_
from pyPgSQL.libpq import PgQuoteString as quote
from pyPgSQL.libpq import OperationalError

from paella.base import Error, debug, NoExistError
from paella.base.util import ujoin
from paella.sqlgen.statement import Statement
from paella.sqlgen.clause import Eq

from lowlevel import CommandCursor

class ColonelCursor(CommandCursor):
    def __init__(self, conn, name=None):
        CommandCursor.__init__(self, conn, name=name)

class StatementCursor(CommandCursor):
    def __init__(self, conn, name=None):
        CommandCursor.__init__(self, conn, name=name)
        self.stmt = Statement('select')

    def set_table(self, table):
        self.stmt.table = table

    def set_clause(self, items, cmp='=', join='and'):
        self.stmt.set_clause(items, cmp=cmp, join=join)

    def set_data(self, data):
        self.stmt.set(data)

    def set_fields(self, fields):
        self.stmt.fields = fields

    def delete(self, table=None, clause=None):
        query = self.stmt.delete(table=table, clause=clause)
        self.execute(query)

    def insert(self, table=None, data=None):
        query = self.stmt.insert(table=table, data=data)
        self.execute(query)

    def update(self, table=None, data=None, clause=None):
        query = self.stmt.update(table=table, data=data, clause=clause)
        self.execute(query)

    def select(self, fields=None, table=None, clause=None,
               group=None, having=None, order=None):
        query = self.stmt.select(fields=fields, table=table, clause=clause,
                                 group=group, having=having, order=order)
        self.execute(query)
        return self.fetchall()

    def iselect(self, fields=None, table=None, clause=None,
               group=None, having=None, order=None):
        query = self.stmt.select(fields=fields, table=table, clause=clause,
                                 group=group, having=having, order=order)
        self.execute(query)
        self._already_selected = True
        return self

    def select_row(self, fields=None, table=None, clause=None,
               group=None, having=None, order=None):
        query = self.stmt.select(fields=fields, table=table, clause=clause,
                                 group=group, having=having, order=order)
        self.execute(query)
        rows = len(self)
        if rows == 1:
            return self.next()
        elif rows == 0:
            raise NoExistError
        else:
            raise Error, 'bad row count %s' % rows

     
    def delete_file(self, conn, field, clause):
        row = self.select_row(fields=[field], clause=clause)
        conn.removefile(int(row[field].name))
        
    def update_file(self, conn, field, clause, fileobj):
        self.delete_file(conn, field, clause)
        newfile = self.file(conn)
        update = {field :newfile.name}
        newfile.write(fileobj.read())
        newfile.close()
        self.update(data=update, clause=clause)

    def open_file(self, conn, field, clause):
        row = self.select_row(fields=[field], clause=clause)
        return self.openfile(conn, row[field].name)
        
    def clear(self, **args):
        self.stmt.clear(**args)

    def fields(self, table=None):
        if table is None:
            table = self.stmt.table
        return CommandCursor.fields(self, table)

    def commit(self):
        CommandCursor.commit(self)

class _TableDict(object):
    def __init__(self, conn, table, key_field='name', value_field='value'):
        object.__init__(self)
        self.conn = conn
        self.cursor = StatementCursor(self.conn)
        self.__key_field__ = key_field
        self.__value_field__ = value_field
        self.cursor.set_table(table)

    def __contains__(self, key):
        return key in self.keys()

    def __len__(self):
        return len(self.keys())

    def items(self):
        fields = [self.__key_field__, self.__value_field__]
        return self.cursor.select(fields, order=self.__key_field__)
        
    def keys(self):
        return [k for k, v in self.items()]

    def values(self):
        return [v for k, v in self.items()]
        
    def has_key(self, key):
        return key in self.keys()

    def update(self, data):
        for k, v in data.items():
            self[k] = v
    
    def __len__(self):
        return len(self.keys())


    def clear(self):
        self.cursor.delete()

    def __repr__(self):
        return str(dict(self.items()))
    
class TableDict(_TableDict):
    def __getitem__(self, key):
        rows = self.cursor.select(fields=[self.__value_field__],
                                  clause=self._single_clause_(key))
        if len(rows) == 1:
            return rows[0][self.__value_field__]
        else:
            raise Error, 'key problem'

    def __setitem__(self, key, value):
        if key in self.keys():
            self.cursor.update(data={self.__value_field__ : value},
                               clause=self._single_clause_(key))
        else:
            self.cursor.insert(data={self.__key_field__ : key,
                                     self.__value_field__ : value})

    def __delitem__(self, key):
        self.cursor.delete(clause=self._single_clause_(key))


    
    def _single_clause_(self, key):
        return '%s = %s' % (self.__key_field__, quote(key))

class TableRowDict(_TableDict):
    def __init__(self, conn, table, key):
        _TableDict.__init__(self, conn, table, key_field=key)

    def __getitem__(self, key):
        rows = self.cursor.select(clause=self._single_clause_(key))
        if len(rows) == 1:
            return rows[0]
        else:
            raise Error, 'key problem'

    def __setitem__(self, key, value):
        if key in self.keys():
            self.cursor.update(data=value,
                               clause=self._single_clause_(key))
        else:
            self.cursor.insert(data=value)

    def __delitem__(self, key):
        self.cursor.delete(clause=self._single_clause_(key))

    def keys(self):
        rows = self.cursor.select(fields=[self.__key_field__],
                                  order=self.__key_field__)
        return [r[self.__key_field__] for r in rows]

    def values(self):
        return self.cursor.select(order=self.__key_field__)
    
    def _single_clause_(self, key):
        return '%s = %s' % (self.__key_field__, quote(key))


class BaseEnvironment(_TableDict):
    def __getitem__(self, key):
        rows = self.cursor.select(fields=[self.__value_field__],
                                  clause=self._double_clause_(key))
        if len(rows) == 1:
            return rows[0][self.__value_field__]
        else:
            raise Error, 'key problem'

    def __setitem__(self, key, value):
        try:
            self.cursor.insert(data={self.__main_field__ : self.__main_value__,
                                     self.__key_field__ : key,
                                     self.__value_field__ : value})
        except OperationalError:
            self.cursor.update(data={self.__value_field__ : value},
                               clause=self._double_clause_(key))
            
    def __delitem__(self, key):
        self.cursor.delete(clause=self._double_clause_(key))

    def keys(self):
        rows = self.cursor.select(fields=[self.__key_field__],
                                  clause=self._single_clause_(),
                                  order=self.__key_field__)
        return [r[self.__key_field__] for r in rows]

    def values(self):
        rows = self.cursor.select(fields=[self.__value_field__, self.__key_field__],
                                  clause=self._single_clause_(),
                                  order=self.__key_field__)
        return [r[self.__value_field__] for r in rows]

    def items(self):
        rows = self.cursor.select(fields=[self.__key_field__, self.__value_field__],
                                  clause=self._single_clause_(),
                                  order=self.__key_field__)
        return [tuple(r) for r in rows]
        

    def clear(self):
        self.cursor.delete(clause=self._single_clause_())

    def _double_clause_(self, key):
        return '%s and %s = %s' %(self._single_clause_(), self.__key_field__, quote(key))

    def _make_superdict_(self, clause):
        superdict = {}
        field = self.__main_field__
        mains = [r[field] for r in self.cursor.select(fields=[field], clause=clause)]
        for m in mains:
            self.set_main(m)
            items = [(m + '_' + key, value) for key, value in self.items()]
            superdict.update(dict(items))
        return superdict
        
class Environment(BaseEnvironment):
    def __init__(self, conn, table, main_field,
                 key_field='name', value_field='value'):
        BaseEnvironment.__init__(self, conn, table,
                                 key_field=key_field, value_field=value_field)
        self.__main_field__ = main_field
        
    def set_main(self, value):
        self.__main_value__ = value

    def _single_clause_(self):
        return '%s = %s' % (self.__main_field__, quote(self.__main_value__))

    
class MultiEnvironment(BaseEnvironment):
    def __init__(self, conn, table, main_fields,
                 key_field='name', value_field='value'):
        if type(main_fields) == str or not len(main_fields) > 1:
            raise Error, 'need at least two fields in a nonstring sequence obj'
        BaseEnvironment.__init__(self, conn, table,
                                 key_field=key_field, value_field=value_field)
        self.__main_fields__ = main_fields

    def set_main(self, *fields):
        self.__main_values__ = [f for f in fields]
        
    def _single_clause_(self):
        nfields = range(len(self.__main_fields__))
        mf, mv = self.__main_fields__, self.__main_values__
        return reduce(and_, [Eq(mf[n], mv[n]) for n in nfields])

    def __setitem__(self, key, value):
        try:
            data = dict(zip(self.__main_fields__, self.__main_values__))
            data[self.__key_field__] = key
            data[self.__value_field__] = value
            print data
            self.cursor.insert(data=data)
        except OperationalError:
            self.cursor.update(data={self.__value_field__ : value},
                               clause=self._double_clause_(key))


class SimpleRelation(object):
    def __init__(self, conn, table, main, name='SimpleRelation'):
        object.__init__(self)
        self.conn = conn
        self.cmd = StatementCursor(self.conn, name)
        self.cmd.set_table(table)
        self._mainfield_ = main
        self.current = None

    def set_current(self, value):
        self.current = value
        self.reset_clause()

    def reset_clause(self, main=None):
        if main is None:
            main = self.current
        if main is not None:
            self.set_clause(main)

    def set_clause(self, main):
        if type(main) is tuple:
            name, value = main
            self.cmd.set_clause([(self._mainfield_, self.current), (name, value)])
        else:
            self.cmd.set_clause([(self._mainfield_, main)])

    def has_it(self, name, value):
        self.set_clause((name, value))
        if len(self.cmd.select()):
            has_it = True
        else:
            has_it = False
        self.reset_clause()
        return has_it

    def get_row(self, name, value):
        self.set_clause((name, value))
        rows = self.cmd.select()
        if len(rows) != 1:
            raise Error, 'incorrect rows in %s' %self.cmd.stmt.table
        return rows[0]

    def delete(self, main):
        self.set_clause(main)
        self.cmd.delete()
        self.reset_clause()

    def diff(self, field, values):
        current_values = Set([x[field] for x in self.cmd.select()])
        diff = list(Set(values) - current_values)
        return diff
    
    def insert(self, field, values):
        diff = self.diff(field, values)
        for value in diff:
            self.insert_relation(field, value)        
        
    def insert_relation(self, field, value):
        insert_data = {self._mainfield_ : self.current,
                       field : value}
        self.cmd.insert(data=insert_data)
        
    

if __name__ == '__main__':
    from lowlevel import QuickConn
    c = QuickConn()
    e = Environment(c, 'woody_variables', 'trait', 'name', 'value')
    cc = StatementCursor(c)

