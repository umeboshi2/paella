#base classes for create table statements, and where clauses
from types import NoneType

def cj_fields(fields):
    if type(fields) == list:
        return ', '.join(fields)
    else:
        return fields

class ColumnType(object):
    def __init__(self, type='text', width=None):
        object.__init__(self)
        self.type = type
        self.width = width

    def __repr__(self):
        if self.width:
            return '%s(%s)' %(self.type, self.width)
        else:
            return '%s' %self.type

class TableColumn(object):
    def __init__(self, table, field):
        object.__init__(self)
        self.table = table
        self.field = field

    def __repr__(self):
        return '%s.%s' % (self.table, self.field)
    
        
class BaseConstraint(object):
    def __init__(self, null=True, unique=None, default=None,
                 pk=None, fk=None, check=None, match=None,
                 delete=None, update=None, defer=None, init=None, auto=None):
        object.__init__(self)
        self.null = null
        self.unique = unique
        self.default = default
        self.default_raw = False
        self.pk = pk
        self.fk = fk
        self.check = check
        self.match = match
        self.delete = delete
        self.update = update
        self.defer = defer
        self.init = init
        self.auto = auto
        self._keylist_ = ['null', 'unique', 'default', 'pk', 'fk', 'check',
                          'match', 'delete', 'update', 'defer', 'init', 'auto']
    def clear(self):
        for k in self._keylist_:
            setattr(self, k, None)
        self.null = True

    def __str__(self):
        return 'foo'

    def __write__(self):
        pass

    def set_fk(self, table, another_name=None):
        if another_name:
            self.fk = '%s (%s)' %(table, another_name)
        else:
            self.fk = table

class UpDelConstraint(BaseConstraint):
    def __init__(self, delete=None, update=None):
        BaseConstraint.__init__(self, delete=delete, update=update)

class KeyConstraint(BaseConstraint):
    def __init__(self, pk=None, fk=None):
        BaseConstraint.__init__(self, pk=pk, fk=fk)

class MiscConstraint(BaseConstraint):
    def __init__(self, check=None, match=None, defer=None,
                 init=None):
        BaseConstraint.__init__(self, check=check, match=match,
                                defer=defer, init=init)

class DefaultConstraint(BaseConstraint):
    def __init__(self, default=None, null=True, unique=None, auto=None):
        BaseConstraint.__init__(self, default=default, null=null,
                                unique=unique, auto=auto)
        
            
        
class Column(object):
    def __init__(self, name, col_type, col_constraint=None, **args):
        self.name = name
        self.type = col_type
        if not col_constraint:
            col_constraint = DefaultConstraint(**args)
        self.constraint = col_constraint

    def __write__(self):
        col = '%s %s' %(self.name, str(self.type))
        con = self.constraint
        if con.null:
            col += ' NULL'
        else:
            col += ' NOT NULL'
        if con.unique:
            col += ' UNIQUE'
        if con.default is not None or con.default == False:
            if con.default_raw:
                col += " DEFAULT %s" % con.default
            else:
                col += " DEFAULT '%s'" % con.default
        if con.check:
            col += ' CHECK %s' % con.check
        if con.fk:
            col += ' REFERENCES %s' % con.fk
        if con.match:
            col += ' MATCH %s' % con.match
        if con.delete:
            col += ' ON DELETE %s' % con.delete
        if con.update:
            col += ' ON UPDATE %s' % con.update
        if con.defer:
            col += ' DEFERRABLE'
        if con.init:
            col += ' INITIALLY %s' % con.init
        return col

    def __repr__(self):
        return self.__write__()

    def __str__(self):
        return self.__write__()

    def set_fk(self, table, another_name=None):
        self.constraint.set_fk(table, another_name)

    def set_auto_increment(self, sequence):
        self.constraint.default = "nextval('%s')" % sequence
        self.constraint.default_raw = True
        

class Table(object):
    def __init__(self, name, columns):
        self.name = name
        self.columns = columns

    def __write__(self):
        cols = cj_fields(map(str, self.columns))
        constraint = self.__pk_constraint__()
        if constraint:
            cols = cj_fields([cols, constraint])
        table = '%s (%s)' % (self.name, cols)
        return table
    
    def __repr__(self):
        return self.__write__()
        
    def __pk_constraint__(self):
        pkeys = []
        for col in self.columns:
            if col.constraint.pk:
                pkeys.append(col.name)
        if len(pkeys):
            flist = '(%s)' %cj_fields(pkeys)
            pkey_constraint = 'primary key %s' %flist
            return pkey_constraint
        else:
            return ''

class Sequence(object):
    def __init__(self, name, start=None, inc=None):
        self.name = name
        self.start = start
        self.inc = inc

    def __repr__(self):
        seq = self.name
        if self.inc is not None:
            seq = '%s INCREMENT %s' % (seq, self.inc)
        if self.start is not None:
            seq = ' %s START %s' % (seq, self.start)
        return seq

class Trigger(object):
    def __init__(self, name, table, function, args=[],
                 when='before', actions=['insert', 'update', 'delete'],
                 each='ROW'):
        self.name = name
        self.table = table
        self.function = function
        self.args = args
        self.when = when
        self.actions = actions
        self.each = each

    def __repr__(self):
        trig = '%s %s %s' % (self.name, self.when, ' OR '.join(self.actions))
        trig = '%s ON %s FOR EACH %s' % (trig, self.table, self.each)
        trig = '%s EXECUTE PROCEDURE %s' % (trig, self.function)
        trig = '%s ( %s )' % (trig, ','.join(self.args))
        return trig

    
if __name__ == '__main__':
    c = Column()
    s = Sequence('itemid')
