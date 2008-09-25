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

from paella import PAELLA_TRAIT_NAME_SEP
from paella.base.objects import VariablesConfig
from paella.base.util import make_deplist

from paella.db.base import SuiteCursor

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

    def make_tagdict(self, family=None, sep='_'):
        if family is not None:
            self.set_family(family)
        fclause = Eq('family', family)
        fields = ['trait', 'name', 'value']
        rows = self.cursor.select(fields=fields, clause=fclause)
        items = [(r.trait + sep + r.name, r.value) for r in rows]
        return dict(items)

    
        
        

class Family(object):
    def __init__(self, conn):
        object.__init__(self)
        self.conn = conn
        self.cursor = StatementCursor(self.conn)
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
            raise Error, 'either pass a family argument or call set_family on this object'
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
        suite_cursor = SuiteCursor(self.conn)
        suites = suite_cursor.get_suites()
        stmt = select_multisuite_union(suites, 'variables')
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
        # change sep here
        sep = PAELLA_TRAIT_NAME_SEP
        # we don't know what to do here
        # it is possible to have an empty
        # list of families, and if that's the
        # case we don't need to make the
        # list of [self.current] .  I need to look
        # for everywhere this method is called.
        # In the installer, the family is never set,
        # and we use the list of families provided
        # by the profile and the machine.  In this
        # case, the families argument will always
        # be a list, empty or not.
        # I can't think of any other circumstance
        # where this method would be called outside
        # of the installer, or a script, and the script
        # should be using either a profile or machine
        # to get the list of families anyway, make the
        # point moot.  I will probably remove this part
        # of the code in the near future, once I'm sure
        # that there's no reason to pass None to the
        # families argument.
        if families is None:
            families = [self.current]
        all = self.make_familylist(families)
        superdict = {}
        for f in all:
            superdict.update(self.env.make_tagdict(f, sep=sep))
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
        # row isn't used, except to determine that the family exists
        row = self.cursor.select_row(table='families', clause=Eq('family', family))
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
        self.report_total_families(len(families))
        for f in families:
            self.write_family(f, path)
            self.report_family_exported(f, path)

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

    def _import_family_xml(self, xmlfile):
        xml = parse_file(xmlfile)
        elements = xml.getElementsByTagName('family')
        if len(elements) != 1:
            raise Error, 'bad number of family tags %s' % len(elements)
        element = elements[0]
        return element
    
            
    def import_family_xml(self, xmlfile):
        element = self._import_family_xml(xmlfile)
        self.import_family(element)
        
    def import_families(self, path):
        xmlfiles = [join(path, x) for x in os.listdir(path) if x[-4:] == '.xml']
        families = []
        for f in xmlfiles:
            element = self._import_family_xml(f)
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
        
    def report_family_exported(self, family, path):
        print 'family %s exported to %s' % (family, path)

    def report_total_families(self, total):
        print 'exporting %d families' % total
        
if __name__ == '__main__':
    pass


