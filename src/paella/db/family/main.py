import os
from os.path import join, dirname, isdir
from sets import Set
from kjbuckets import kjGraph

from xml.dom.minidom import parse as parse_file

from useless.base import ExistsError, Error, debug, UnbornError

from useless.sqlgen.clause import Eq
from useless.sqlgen.statement import Statement
from useless.db.midlevel import StatementCursor, SimpleRelation
from useless.db.midlevel import Environment, MultiEnvironment

from paella.base.objects import VariablesConfig
from paella.base.util import make_deplist

#from base import Suites, make_deplist

from xmlgen import FamilyElement
from xmlparse import FamilyParser

def select_multisuite_union(suites, table, fields=None, clause=None):
    stmt = Statement()
    if fields is not None:
        stmt.fields = fields
    if clause is not None:
        stmt.set_clause(clause)
    stmts = [stmt.select(table='%s_%s' % (s, table)) for s in suites]
    return ' UNION '.join(stmts)


class FamilyVariablesConfig(VariablesConfig):
    def __init__(self, conn, family):
        VariablesConfig.__init__(self, conn, 'family_environment',
                                 'trait', 'family', family)

class FamilyEnvironment(MultiEnvironment):
    def __init__(self, conn):
        MultiEnvironment.__init__(self, conn, 'family_environment',
                                  ['family', 'trait'])
        self.__main_values__ = '',''
        

    def set_family(self, family):
        self.__main_values__ = family, self.__main_values__[1]

    def make_tagdict(self, family=None):
        if family is not None:
            self.set_family(family)
        fclause = Eq('family', family)
        fields = ['trait', 'name', 'value']
        rows = self.cursor.select(fields=fields, clause=fclause)
        items = [(r.trait + '_' + r.name, r.value) for r in rows]
        return dict(items)

    
        
        

class Family(object):
    def __init__(self, conn):
        object.__init__(self)
        self.conn = conn
        #self.suites = Suites(conn).list()
        self.cursor = StatementCursor(self.conn)
        self.suites = [r.suite for r in self.cursor.select(table='suites')]
        self.current = None
        self.parent = SimpleRelation(self.conn, 'family_parent', 'family')
        self.env = FamilyEnvironment(self.conn)
        
    def set_family(self, family):
        self.current = family
        self.parent.set_current(family)
        self.env.set_family(family)

    def _check_family(self, family):
        if family is not None:
            return family
        else:
            family = self.current
        if family is None:
            raise Error, 'either pass a family arguement or call set_family on this object'
        return family
    
    def add_family(self, family, type='general'):
        pass

    def get_related_families(self, families=[]):
        rows = self.cursor.select(table='family_parent')
        graph = kjGraph([(r.family, r.parent) for r in rows])
        dfamilies = Set()
        for fam in families:
            dfamilies |= Set([fam]) | Set(graph.reachable(fam).items())
        return dfamilies

    def parent_rows(self, family=None):
        family = self._check_family(family)
        self.parent.set_clause(family)
        rows = self.parent.cmd.select(fields=['parent'], order='parent')
        self.parent.reset_clause()
        return rows

    def parents(self, family=None):
        family = self._check_family(family)
        rows = self.parent_rows(family)
        return [x.parent for x in rows]
    
    def environment_rows(self, family=None):
        family = self._check_family(family)
        clause = Eq('family', family)
        args = dict(fields=['trait', 'name', 'value'], clause=clause, order=['trait', 'name'])
        return self.env.cursor.select(**args)

    def family_rows(self):
        return self.cursor.select(fields=['family'], table='families', order='family')

    def all_families(self):
        return [r.family for r in self.family_rows()]

    def get_all_defaults(self):
        stmt = select_multisuite_union(self.suites, 'variables')
        print stmt
        self.cursor.execute(stmt)
        return self.cursor.fetchall()

    def create_family(self, family):
        if family not in self.all_families():
            self.cursor.insert(table='families', data=dict(family=family))
        else:
            raise ExistsError, '%s already exists' % family

    def insert_parents(self, parents, family=None):
        family = self._check_family(family)
        self.parent.insert('parent', parents)

    def FamilyData(self, families=[]):
        if families is None:
            families = [self.current]
        all = self.make_familylist(families)
        superdict = {}
        for f in all:
            superdict.update(self.env.make_tagdict(f))
        return superdict
            
        
            
    def make_familylist(self, families):
        deps = families
        all = list(self.get_related_families(families))
        setfun = self.set_family
        parfun = self.parents
        return make_deplist(deps, all, setfun, parfun)

    def export_family(self, family=None):
        if family is None:
            family = self.current
        element = FamilyElement(family)
        element.append_parents(self.parents(family))
        element.append_variables(self.environment_rows(family))
        return element

    def write_family(self, family, path):
        fxml = file(join(path, '%s.xml' % family), 'w')
        data = self.export_family(family)
        data.writexml(fxml, indent='\t', newl='\n', addindent='\t')
        fxml.close()
        
    def export_families(self, path):
        families = self.all_families()
        for f in families:
            self.write_family(f, path)
            

    def import_family(self, element):
        parsed = FamilyParser(element)
        print 'inserting family', parsed.name
        all = self.all_families()
        for p in parsed.parents:
            if p not in all:
                print 'insertion failed for', parsed.name
                raise UnbornError
        self.create_family(parsed.name)
        self.set_family(parsed.name)
        self.insert_parents(parsed.parents)
        row = dict(family=parsed.name)
        for var in parsed.environ:
            row.update(var)
            self.cursor.insert(table='family_environment', data=row)
            
    def import_families(self, path):
        xmlfiles = [join(path, x) for x in os.listdir(path) if x[-4:] == '.xml']
        families = []
        for f in xmlfiles:
            xml = parse_file(f)
            elements = xml.getElementsByTagName('family')
            if len(elements) != 1:
                raise Error, 'bad number of family tags %s' % len(elements)
            element = elements[0]
            families.append(element)
        while len(families):
            f = families[0]
            try:
                self.import_family(f)
            except UnbornError:
                families.append(f)
            del families[0]
        print len(families), 'families inserted'

    def getVariablesConfig(self, family=None):
        family = self._check_family(family)
        return FamilyVariablesConfig(self.conn, family)
    
    def deleteVariable(self, trait, name, family=None):
        family = self._check_family(family)
        data = dict(family=family, trait=trait, name=name)
        clause = reduce(and_, [Eq(k, v) for k,v in data.items()])
        self.env.cursor.delete(clause=clause)

    def insertVariable(self, trait, name, value, family=None):
        family = self._check_family(family)
        data = dict(family=family, trait=trait, name=name)
        clause = reduce(and_, [Eq(k, v) for k,v in data.items()])
        testrows = self.cursor.select(table='family_environment', clause=clause)
        if not len(testrows):
            data['value'] = value
            self.cursor.insert(table='family_environment', data=data)
        
    
if __name__ == '__main__':
    import os
    from base import PaellaConnection
    conn = PaellaConnection()
    #path = g['db_bkup_path']
    #db = XmlDatabase(conn, path)
    #p = ProfileStruct
    #t = _Trait_(conn, 'woody')
    #ts = Traits(conn, 'woody')
    #t.set('default')
    #ss = parse_string(t.toxml())
    #tp = TraitParser(ss.firstChild)
    #pd = PaellaDatabase(conn, path)
    #pp = PaellaProcessor(conn)
    #pp.parse_xml('foo.xml')
    f = Family(conn)

    #cmd = CommandCursor(c, 'dsfsdf')
    cmd = StatementCursor(conn)
    def dtable():
        cmd.execute('drop table ptable')

    def dtables():
        for t in cmd.tables():
            if t != 'footable':
                cmd.execute('drop table %s' %t)


