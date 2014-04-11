#from useless.sqlgen.clause import Eq
#from useless.db.midlevel import StatementCursor

from paella.db import DefaultEnvironment
from paella.db import CurrentEnvironment

class InstallerManager(object):
    def __init__(self, conn):
        self.conn = conn
        self.defenv = DefaultEnvironment(conn)

    def get_known_machines(self):
        machines = []
        macs = self.defenv.options('machines')
        for mac in macs:
            machine = self.defenv.get('machines', mac)
            if machine not in machines:
                machines.append(machine)
        return machines

    def approve_machine(self, machine):
        env  = self.get_current_environment(machine)
        

    def get_current_environment(self, machine):
        env = CurrentEnvironment(self.conn)
        env.change(machine)
        return env
    
