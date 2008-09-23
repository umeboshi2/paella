from os.path import join
from xml.dom.minidom import parseString

from useless.base import NoExistError, UnbornError
from useless.base.path import path
from useless.base.util import makepaths

from useless.db.midlevel import StatementCursor
from useless.sqlgen.clause import Eq

from paella.db.family import Family

from base import DiskConfigHandler
from base import BaseMachineHandler

from relations import MachineRelations
#from xmlparse import MachineDatabaseParser
#from xmlgen import MachineDatabaseElement
from xmlgen import MachineElement
from xmlgen import KernelsElement
from xmlgen import MachineDatabaseElement
from xmlparse import MachineDatabaseParser
from xmlparse import MachineParser



class MachineHandler(BaseMachineHandler):
    def __init__(self, conn):
        BaseMachineHandler.__init__(self, conn)
        self.relation = MachineRelations(self.conn)
        self.family = Family(self.conn)
        self.parent = None
        self.diskconfig = None
        self.kernel = None
        
    def set_machine(self, machine):
        BaseMachineHandler.set_machine(self, machine)
        self.relation.set_machine(machine)
        self.parent = self.relation.parents.get_parent()
        
    def add_new_kernel(self, kernel):
        if self._check_kernel_exists(kernel):
            self.relation.kernels.insert(data=dict(kernel=kernel))
        else:
            msg = "There's no kernel named %s in the package list" % kernel
            raise RuntimeError , msg
            
    def make_a_machine(self, machine):
        data = dict(machine=machine)
        self.cursor.insert(table='machines', data=data)

    def get_machine_list(self):
        rows = self.cursor.select(table='machines', order='machine')
        return [row.machine for row in rows]
    
    def set_parent(self, parent):
        self._check_machine_set()
        self.relation.parents.set_parent(parent)
        # reset the attributes here
        self.set_machine(self.current_machine)

    def delete_parent(self):
        self._check_machine_set()
        self.relation.parents.delete_parent()
        self.set_machine(self.current_machine)
        

    def _get_attribute(self, attribute, show_inheritance=False):
        self._check_machine_set()
        attribute_value = getattr(self, attribute)
        if attribute_value is None:
            return self.relation.get_attribute(attribute, show_inheritance=show_inheritance)
        if show_inheritance:
            return attribute_value, None
        else:
            return attribute_value

    def get_attribute(self, attribute, show_inheritance=True):
        """This method should be used from the gui, so
        show_inheritance is implied as True."""
        return self._get_attribute(attribute, show_inheritance=show_inheritance)

    def set_attribute(self, attribute, value):
        self._check_machine_set()
        if attribute == 'kernel':
            self.set_kernel(value)
        elif attribute == 'profile':
            self.set_profile(value)
        elif attribute == 'diskconfig':
            self.set_diskconfig(value)
        else:
            raise RuntimeError , "unknown attribute %s in set_attribute" % attribute
        
    #########################
    # for these methods, inheritance
    # is presumed, if you only need
    # the values set for the current
    # machine, just use the attribute
    # values -> self.attribute
    #########################
    def get_diskconfig(self, show_inheritance=False):
        return self._get_attribute('diskconfig', show_inheritance=show_inheritance)

    def get_kernel(self, show_inheritance=False):
        return self._get_attribute('kernel', show_inheritance=show_inheritance)

    def get_profile(self, show_inheritance=False):
        return self._get_attribute('profile', show_inheritance=show_inheritance)

    #########################
    # convenience methods for installer
    #########################
    
    def get_diskconfig_content(self):
        diskconfig = self.get_diskconfig()
        content = self.relation.diskconfig.get(diskconfig).content
        return content

    def get_machine_data(self):
        self._check_machine_set()
        return self.relation.get_superdict()
    
    #########################
    # Import/Export methods
    #########################

    # due to the way ScriptCursor is
    # written, we need to have the
    # machine set before exporting it.
    # Either that, or override more ScriptCursor
    # method.
    def export_machine(self, exportdir):
        self._check_machine_set()
        element = MachineElement(self.conn, self.current_machine)
        exportdir = path(exportdir)
        element.export(exportdir)
        subdir = element.export_directory(exportdir)
        self.relation.scripts.export_scripts(subdir)

    def export_kernels(self, exportdir):
        element = KernelsElement(self.conn)
        exportdir = path(exportdir)
        filename = exportdir / 'kernels.xml'
        xmlfile = file(filename, 'w')
        xmlfile.write(element.toprettyxml())
        xmlfile.close()

    # if no machine is set when this is
    # called, it will be set to the last
    # machine that's exported.  Here,
    # the exportdir is assumed to be
    # the "machines" directory in the
    # main database, but it doesn't
    # need to be if it's called outside
    # of "export_machine_database"
    def export_all_machines(self, exportdir):
        current_machine = self.current_machine
        for machine in self.get_machine_list():
            self.set_machine(machine)
            self.export_machine(exportdir)
        if current_machine is not None:
            self.set_machine(current_machine)

    def export_machine_database(self, exportdir):
        element = MachineDatabaseElement(self.conn)
        exportdir = path(exportdir)
        makepaths(exportdir)
        filename = exportdir / 'machine_database.xml'
        xmlfile = file(filename, 'w')
        xmlfile.write(element.toprettyxml())
        xmlfile.close()
        machine_dir = exportdir / 'machines'
        self.export_all_machines(machine_dir)

    def import_machine_database(self, importdir):
        importdir = path(importdir)
        mdb_filename = importdir / 'machine_database.xml'
        if not mdb_filename.exists():
            raise RuntimeError , "%s doesn't exist" % mdb_filename
        doc_element = parseString(mdb_filename.text())
        mdb_element = doc_element.firstChild
        tagName = mdb_element.tagName.encode()
        if tagName != 'machine_database':
            msg = "This doesn't seem to be the proper xml file.\n"
            msg += "The main tag is %s instead of machine_database.\n" % name
            raise RuntimeError , msg
        mdb_parser = MachineDatabaseParser(importdir, mdb_element)
        for kernel in mdb_parser.kernels:
            print "inserting kernel", kernel
            self.add_new_kernel(kernel)
        machines_dir = importdir / 'machines'
        self.import_machines(mdb_parser.machines, machines_dir)
        

    # machines is a list of names (generally taken
    # from the machine_database xml file).  The
    # dirname is the "machines" directory, where
    # there is a directory for each machine named
    # after the names in the list.
    def import_machines(self, machines, dirname):
        dirname = path(dirname)
        current_machine = self.current_machine
        # make a queue for the machines
        machine_queue = [machine for machine in machines]
        # I hope this is correct.  This is an
        # attempt to keep this function from
        # running in an infinite loop.
        num_machines = len(machine_queue)
        max_loops = (num_machines * (num_machines +1) ) / 2
        count = 0
        while machine_queue:
            machine = machine_queue.pop(0)
            machine_dir = dirname / machine
            try:
                self.import_machine(machine_dir)
            except UnbornError:
                print "machine %s hasn't been imported yet."
                machine_queue.append(machine)
            count +=1
            if count > max_loops:
                msg = "We appear to be in an infinite loop.\n"
                msg += "It's likely that there are unmet dependencies"
                msg += " in your list of machines."
                raise RuntimeError , msg
        if current_machine is not None:
            self.set_machine(current_machine)
            
        
    def import_machine(self, dirname):
        dirname = path(dirname)
        current_machine = self.current_machine
        parser = self._parse_machine_xml(dirname)
        machine = parser.machine
        imported_machines = self.get_machine_list()
        if machine.parent is not None:
            if machine.parent not in imported_machines:
                raise UnbornError, "%s not imported yet." % machine.parent
        self.make_a_machine(machine.name)
        self.set_machine(machine.name)
        # attributes - these will fail with foreign key
        # errors if they're not present in the database
        self.set_profile(machine.profile)
        self.set_kernel(machine.kernel)
        self.set_diskconfig(machine.diskconfig)
        if machine.parent is not None:
            self.set_parent(machine.parent)
        for family in machine.families:
            print "import family", family
            self.relation.family.append_family(family)
        for scriptname in machine.scripts:
            script_filename ='script-%s' % scriptname
            script_filename = dirname / script_filename
            print "import script", scriptname, script_filename
            self.relation.scripts.insert_script(scriptname, file(script_filename))
        for trait, name, value in machine.variables:
            print "import machine_variable -> %s", tuple((trait, name, value))
            self.relation.environment.append_variable(trait, name, value)
        # all done, set machine back to what it was,
        # unless it wasn't set in the first place, then
        # it remains set to what was just imported
        if current_machine is not None:
            self.set_machine(current_machine)
            
        
            
    def _parse_machine_xml(self, dirname):
        dirname = path(dirname)
        xml_filename = dirname / 'machine.xml'
        doc_element = parseString(xml_filename.text())
        machine_element = doc_element.firstChild
        tagName = machine_element.tagName.encode()
        if tagName != 'machine':
            msg = "This doesn't seem to be the proper xml file.\n"
            msg += "The main tag is %s instead of machine.\n" % name
            raise RuntimeError , msg
        parser = MachineParser(machine_element)
        return parser
    
    #########################
    # some convenience methods for
    # the gui
    #########################
    def list_all_kernels(self):
        """convenience method for helping select a kernel
        for a machine in the gui"""
        return [r.kernel for r in self.kernels.select()]

    def list_all_profiles(self):
        """convenience method for helping select a profile
        for a machine in the gui"""
        rows = self.cursor.select(table='profiles')
        return [r.profile for r in rows]

    def list_all_diskconfigs(self):
        """convenience method for helping select a diskconfig
        for a machine in the gui"""
        rows = self.cursor.select(fields=['name'], table='diskconfig')
        return [row.name for row in rows]
    
if __name__ == '__main__':
    from os.path import join
    from paella.db import PaellaConnection
    conn = PaellaConnection()
