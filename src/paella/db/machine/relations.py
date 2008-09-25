from os.path import join
from xml.dom.minidom import parseString

from useless import deprecated
from useless.base.util import strfile
from useless.base import NoExistError
from useless.db.midlevel import StatementCursor, Environment
from useless.sqlgen.clause import Eq, In

from paella import PAELLA_TRAIT_NAME_SEP
from paella.base.util import edit_dbfile
from paella.base.objects import VariablesConfig
from paella.db.base import ScriptCursor
from paella.db.family import Family

from base import DiskConfigHandler
from base import BaseMachineDbObject
from base import Table_cursor


import warnings
class NotReadyYetWarning(Warning):
    pass

warnings.simplefilter('always', NotReadyYetWarning)

class AttributeUnsetInAncestryError(RuntimeError):
    """Error to declare that the attribute isn't set
    anywhere in the ancestry."""
    pass

class MachineVariablesConfig(VariablesConfig):
    def __init__(self, conn, machine):
        VariablesConfig.__init__(self, conn, 'machine_variables',
                                 'trait', 'machine', machine)


# Unlike, traits and families, a machine
# can only have one parent.
class MachineParents(BaseMachineDbObject):
    def __init__(self, conn):
        BaseMachineDbObject.__init__(self, conn, table='machine_parent')
        
    def get_parent(self, machine=None):
        if machine is None:
            self._check_machine_set()
            machine = self.current_machine
        clause = Eq('machine', machine)
        try:
            row = self.cursor.select_row(clause=clause)
            return row.parent
        except NoExistError:
            return None
    
    def set_parent(self, parent, machine=None):
        data = dict(parent=parent)
        if machine is None:
            self._check_machine_set()
            machine = self.current_machine
        if parent == machine:
            raise RuntimeError , "Machine can't be it's own parent"
        if self.get_parent(machine=machine) is None:
            # if there's not already a parent we
            # insert a new one
            data['machine'] = machine
            self.cursor.insert(data=data)
        else:
            # else we update it
            clause = Eq('machine', machine)
            self.cursor.update(data=data, clause=clause)

    def delete_parent(self, machine=None):
        if machine is None:
            self._check_machine_set()
            machine = self.current_machine
        clause = Eq('machine', machine)
        self.cursor.delete(clause=clause)

    def has_children(self, machine=None):
        if machine is None:
            self._check_machine_set()
            machine = self.current_machine
        clause = Eq('parent', machine)
        rows = self.cursor.select(clause=clause)
        return len(rows)
    
    def get_parent_list(self, childfirst=True, machine=None):
        if machine is None:
            self._check_machine_set()
            machine = self.current_machine
        parents = []
        parent = self.get_parent(machine=machine)
        while parent is not None:
            parents.append(parent)
            parent = self.get_parent(machine=parent)
        if not childfirst:
            parents.reverse()
        return parents
    
            
class MachineScripts(ScriptCursor, BaseMachineDbObject):
    def __init__(self, conn):
        ScriptCursor.__init__(self, conn, 'machine_scripts', 'machine')
        # we need this from BaseMachineDbObject
        # but we can't call BaseMachineDbObject.__init__
        # since this class is subclassed from a cursor
        self.current_machine = None
        # we hope that having this cursor in a cursor
        # doesn't cause problems.  We really need
        # to consider turning the ScriptCursor into
        # a subclass of object and including a cursor
        # member.
        self.cursor = conn.cursor(statement=True)
        #self._parents = MachineParents(conn)
        
        # we don't expect to change any of the
        # scriptnames during the life of this object
        # so we make a static list to keep from
        # talking to the database everytime we
        # need this list.  If we ever make code to
        # mess with the script list, we'll need an
        # "update_scriptnames" method to update
        # this list.  This list is being used to help
        # the gui determine what scripts to look
        # for in the machine parents.  The installer
        # won't need this, since each step in the
        # installer will look for a script, but the
        # gui doesn't do that.
        self.scriptnames = self._list_scriptnames()

    def set_machine(self, machine):
        BaseMachineDbObject.set_machine(self, machine)
        #self._parents.set_machine(machine)
        
    def _clause(self, name, machine=None):
        if machine is None:
            self._check_machine_set()
            machine = self.current_machine
        clause = Eq(self._keyfield, machine) & Eq('script', name)
        return clause

    def insert_script(self, name, scriptfile, machine=None):
        if machine is None:
            self._check_machine_set()
            machine = self.current_machine
        self._insert_script(name, scriptfile, machine)

    def scripts(self, machine=None):
        if machine is None:
            self._check_machine_set()
            machine = self.current_machine
        clause  = Eq('machine', machine)
        return self.select(clause=clause)

    # Note that this method talks to the
    # database more often then is actually
    # necessary.  We override this method
    # from ScriptCursor so that we can pass
    # the machine argument, in order to the
    # script from the machine parents.
    def get(self, name, machine=None):
        if machine is None:
            self._check_machine_set()
            machine = self.current_machine
        clause = self._clause(name, machine=machine)
        #print clause
        rows = self.select(clause=clause)
        if len(rows) == 1:
            #print rows
            return self.scriptfile(name, machine=machine)
        else:
            return None

    # override this method to allow for passing
    # the machine argument.  All the methods
    # being overridden, as well as the other
    # problems with ScriptCursor is a good
    # indication that it needs to be rewritten
    # entirely.
    def _script_row(self, name, machine=None):
        if machine is None:
            self._check_machine_set()
            machine = self.current_machine
        clause = self._clause(name, machine=machine)
        table = self._jtable
        return self.select_row(fields=['*'], table=table, clause=clause)

    def scriptdata(self, name, machine=None):
        if machine is None:
            self._check_machine_set()
            machine = self.current_machine
        return self._script_row(name, machine=machine).data

    def scriptfile(self, name, machine=None):
        if machine is None:
            self._check_machine_set()
            machine = self.current_machine
        return strfile(self.scriptdata(name, machine=machine))

    def _list_scriptnames(self):
        table = 'scriptnames'
        clause = In('type', ['both', 'machine'])
        rows = self.cursor.select(fields=['script'], table=table, clause=clause)
        return [row.script for row in rows]
    
    
class MachineFamily(BaseMachineDbObject):
    def __init__(self, conn):
        BaseMachineDbObject.__init__(self, conn, table='machine_family')
        #self._parents = MachineParents(self.conn)
        
    def set_machine(self, machine):
        BaseMachineDbObject.set_machine(self, machine)
        #self._parents.set_machine(machine)
        
    def family_rows(self, machine=None):
        if machine is None:
            self._check_machine_set()
            machine = self.current_machine
        clause = Eq('machine', machine)
        return self.cursor.select(clause=clause, order='family')

    def delete_family(self, family, machine=None):
        if machine is None:
            self._check_machine_set()
            machine = self.current_machine
        clause = Eq('machine', machine) & Eq('family', family)
        self.cursor.delete(clause=clause)

    def append_family(self, family, machine=None):
        if machine is None:
            self._check_machine_set()
            machine = self.current_machine
        data = dict(machine=machine, family=family)
        self.cursor.insert(data=data)

    def get_families(self, machine=None):
        rows = self.family_rows(machine=machine)
        return [row.family for row in rows]
        
class MachineEnvironment(BaseMachineDbObject, Environment):
    def __init__(self, conn):
        BaseMachineDbObject.__init__(self, conn, table='machine_variables')
        Environment.__init__(self, conn, 'machine_variables', 'trait')
        self._parents = MachineParents(self.conn)

    def __repr__(self):
        return "<MachineEnvironment: %s>" % self.current_machine

    def _make_superdict_(self):
        msg = "_make_superdict_ is not really ready yet"
        warnings.warn(msg, NotReadyYetWarning, stacklevel=3)
        clause = self._machine_clause_()
        return Environment._make_superdict_(self, clause)

    def make_superdict(self, machine=None):
        # change sep here
        sep = PAELLA_TRAIT_NAME_SEP
        msg = 'make_superdict is not really ready yet'
        warnings.warn(msg, NotReadyYetWarning, stacklevel=3)
        if machine is None:
            self._check_machine_set()
            machine = self.current_machine
        clause = self._machine_clause_(machine=machine)
        # due to limitations in the Environment class
        # we need to temporarily set the machine
        # to the value of the machine argument, then
        # set it back before returning the superdict
        current_machine = self.current_machine
        self.set_machine(machine)
        superdict = Environment.make_superdict(self, clause, sep=sep)
        self.set_machine(current_machine)
        return  superdict
        
    def set_machine(self, machine):
        BaseMachineDbObject.set_machine(self, machine)
        self._parents.set_machine(machine)
        
    def _single_clause_(self):
        return Eq('machine', self.current_machine) & Eq('trait', self.__main_value__)

    def append_variable(self, trait, name, value):
        self._check_machine_set()
        data = dict(machine=self.current_machine,
                    trait=trait, name=name, value=value)
        self.cursor.insert(data=data)

    def delete_variable(self, trait, name):
        self._check_machine_set()
        clause = Eq('machine', self.current_machine) & Eq('trait', trait) \
                 & Eq('name', name)
        self.cursor.delete(clause=clause)

    def update_variable(self, trait, name, value):
        self._check_machine_set()
        clause = Eq('machine', self.current_machine) & Eq('trait', trait) \
                 & Eq('name', name)
        data = dict(value=value)
        self.cursor.update(data=data, clause=clause)
        
class MachineRelations(BaseMachineDbObject):
    "Class to hold the relations"
    def __init__(self, conn):
        BaseMachineDbObject.__init__(self, conn, table='machines')
        self.parents = MachineParents(self.conn)
        self.scripts = MachineScripts(self.conn)
        self.family = MachineFamily(self.conn)
        self.environment = MachineEnvironment(self.conn)
        self.config = None
        # These aren't really actual relations in the
        # same sense that the above objects are
        # but they are objects the the machines
        # table relates to, and should fit nicely in this
        # class.
        self.diskconfig = DiskConfigHandler(self.conn)
        self.kernels = Table_cursor(self.conn, 'kernels')
        # This is the main family class
        self.mainfamily = Family(self.conn)
        
    def set_machine(self, machine):
        BaseMachineDbObject.set_machine(self, machine)
        self.parents.set_machine(machine)
        self.scripts.set_machine(machine)
        self.family.set_machine(machine)
        self.environment.set_machine(machine)
        self.config = MachineVariablesConfig(self.conn, machine)

    def get_families(self, inherited=False, show_inheritance=False, machine=None):
        if machine is None:
            self._check_machine_set()
            machine = self.current_machine
        if show_inheritance:
            inherited = True
        families = self.family.get_families(machine=machine)
        if inherited:
            famlist = []
            parents = self.parents.get_parent_list(childfirst=False)
            for parent in parents:
                pfam = self.family.get_families(parent)
                if pfam:
                    famlist.append((parent, pfam))
            if show_inheritance:
                return families, famlist
            else:
                for parent, pfam in famlist:
                    for family in pfam:
                        if family not in families:
                            families.append(family)
        return families

    def get_script(self, name, inherited=False, show_inheritance=False):
        scriptfile = self.scripts.get(name)
        if show_inheritance:
            inherited = True
        # if we get the scriptfile without checking
        # through the parents, we go ahead and return
        # it
        if scriptfile is not None:
            if show_inheritance:
                return scriptfile, None
            else:
                return scriptfile
        # if we get here, the scriptfile is None
        # so we need to check through the parents.
        if not inherited:
            # if we're not asking for inheritance, we
            # go ahead and return the scriptfile
            return scriptfile
        else:
            # otherwise, we traverse the parents looking
            # for the script
            parents = self.parents.get_parent_list(childfirst=True)
            for parent in parents:
                scriptfile = self.scripts.get(name, parent)
                #print parent, scriptfile
                if scriptfile is not None:
                    if show_inheritance:
                        return scriptfile, parent
                    else:
                        return scriptfile
            # if we didn't find a script above, there isn't one
            # and we return None
            return None

    def edit_script(self, name):
        self._check_machine_set()
        scriptfile = self.get_script(name, inherited=False)
        if scriptfile is not None:
            content = edit_dbfile(name, scriptfile.read(), 'script')
            if content is not None:
                self.scripts.save_script(name, strfile(content))

    def _get_row(self, machine):
        clause = self._machine_clause_(machine)
        return self.cursor.select_row(clause=clause)

    # this is the helper function for determining
    # the diskconfig, kernel, or profile
    def get_attribute(self, attribute, show_inheritance=False):
        parents = self.parents.get_parent_list(childfirst=True)
        for parent in parents:
            row = self._get_row(parent)
            if row[attribute] is not None:
                if show_inheritance:
                    return row[attribute], parent
                else:
                    return row[attribute]
        # there's a probem if the for loop completes without
        # finding the attribute.
        msg = "%s must be set somewhere in the hierarchy of machines" % attribute
        raise AttributeUnsetInAncestryError, msg

    # we may require the machine to be set later
    # but for now, we can get the superdict with
    # an optional machine argument.
    # FIXME: we need to include families here.
    def get_superdict(self, machine=None):
        if machine is None:
            self._check_machine_set()
            machine = self.current_machine
        # childfirst is False because we go from top down
        # here, to get the child to override the parent
        parents = self.parents.get_parent_list(childfirst=False, machine=machine)
        superdict = dict()
        for parent in parents:
            parent_families = self.get_families(machine=parent)
            famdata = self.mainfamily.FamilyData(families=parent_families)
            superdict.update(famdata)
            superdict.update(self.environment.make_superdict(machine=parent))
        families = self.get_families(machine=machine)
        famdata = self.mainfamily.FamilyData(families=families)
        superdict.update(famdata)
        superdict.update(self.environment.make_superdict(machine=machine))
        return superdict
    
if __name__ == '__main__':
    from os.path import join
    from paella.db import PaellaConnection
    conn = PaellaConnection()
    pmtypes = ['ggf', 'gf', 'f', 's', 'gs', 'ggs']
    mp = MachineTypeParent(conn)
    mt = MachineTypeHandler(conn)
    
