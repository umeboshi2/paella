from copy import deepcopy

from classes import ColumnType, KeyConstraint, DefaultConstraint
from classes import Column, Table, Sequence, Trigger

#blanks
_unique = '__unique__'
_null = '__NULL__'
_unref = '__unref__'


#types
NUM = ColumnType('int')
NAME = ColumnType('varchar', 50)
BIGNAME = ColumnType('varchar', 255)
SMALLNAME = ColumnType('varchar', 20)
BOOL = ColumnType('bool')
DATETIME = ColumnType('timestamp')
TEXT = ColumnType('text')
MONEY = ColumnType('float8')
FL53 = ColumnType('numeric', (5,3))
INET = ColumnType('inet')
MAC = ColumnType('macaddr')
OID = ColumnType('oid')

###############
#Sequences
###############
class ActionIdentifier(Sequence):
    def __init__(self):
        Sequence.__init__(self, 'lp_seq_actionid')

class ActionTrigger(Trigger):
    def __init__(self, table):
        trigname = 'lp_tgr_%s' % table
        Trigger.__init__(self, trigname, table, 'action_stamp')

class ActionFunction(object):
    def __init__(self, name):
        self.name = name
        self.decs = []
        self.stmts = []

    def __repr__(self):
        return 'hello there'
    
    
        
###############
#Columns
###############
def AutoId(name):
    column = Column(name, NUM)
    c = column.constraint
    c.pk = 1
    c.unique = 1
    c.auto = 1
    c.null = 0
    return column


def DefaultNamed(name, default):
    column = Column(name, NAME)
    column.constraint.default = default
    return column

def Pk(name, type):
    column = Column(name, type)
    column.constraint.pk = 1
    return column

def PkName(name):
    return Pk(name, NAME)

def PkBigname(name):
    return Pk(name, BIGNAME)

def PkNum(name):
    return Pk(name, NUM)

def Name(name):
    return Column(name, NAME)

def Bigname(name):
    return Column(name, BIGNAME)

def Num(name):
    return Column(name, NUM)

def Text(name):
    return Column(name, TEXT)

def Bool(name, default=False):
    column = Column(name, BOOL)
    column.constraint.default = default
    column.constraint.null = False
    return column

def Oid(name):
    return Column(name, OID)

def DateTime(name):
    dt = Column(name, DATETIME)
    dt.constraint.default = 'now()'
    return dt

def make_default_log_columns():
    actionid = PkNum('actionid')
    actionid.constraint.default = "nextval('lp_seq_actionid')"
    actionid.constraint.default_raw = True
    action = Name('action')
    action.constraint.null = False
    modtime = DateTime('modtime')
    modtime.constraint.null = False
    modtime.constraint.default = 'now()'
    modtime.constraint.default_raw = True
    return [actionid, action, modtime]

###############
#Tables
###############
class PkBNameNullDefaults(Table):
    def __init__(self, name, columns, pk):
        ncols = []
        for col in columns:
            if col != pk:
                ncols.append(Column(col, BIGNAME))
            else:
                pkcol = Column(col, BIGNAME)
                pkcol.constraint.pk = 1
                ncols[0:0] = [pkcol]
        Table.__init__(self, name, ncols)

class NameTable(Table):
    def __init__(self, name, columns):
        columns = [Name(field) for field in columns]
        Table.__init__(self, name, columns)

class BignameTable(Table):
    def __init__(self, name, columns):
        columns = [Bigname(field) for field in columns]
        Table.__init__(self, name, columns)


#single column master tables
class PkBignameTable(Table):
    def __init__(self, tablename, fieldname):
        Table.__init__(self, tablename, [PkBigname(fieldname)])

class PkNameTable(Table):
    def __init__(self, tablename, fieldname):
        Table.__init__(self, tablename, [PkName(fieldname)])
        

class RelationalTable(Table):
    def __init__(self, tablename, related_table, primary_column, other_columns):
        primary_column.set_fk(related_table)
        Table.__init__(self, tablename, [primary_column] + other_columns)

class LogTable(Table):
    def __init__(self, table):
        if not issubclass(table.__class__, Table):
            raise Error, 'need to pass a Table'
        table = deepcopy(table)
        #remove constraints from original table's columns
        for col in table.columns:
            col.constraint.clear()
        table.columns += make_default_log_columns()
        tablename = 'lp_log_' + table.name
        Table.__init__(self, tablename, table.columns)
        

if __name__ == '__main__':
    f = AutoId
    c = Column('fname', NAME)
    #t = Table()
    dn = DefaultNamed('foo', 'bar')
    ai = AutoId('dd')
    cols = ['a','b','c','d']
    pkt = PkBNameNullDefaults
    
    
