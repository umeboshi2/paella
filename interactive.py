import os
from paella.base import PaellaConfig
from paella.db import PaellaConnection
from paella.db.trait import Trait
from paella.db.family import Family
from paella.db.profile import Profile
from paella.db.machine import MachineHandler

from paella.db import DefaultEnvironment

from paella.installer.toolkit import InstallerTools

if __name__ == '__main__':
    cfg = PaellaConfig()
    conn = PaellaConnection()
    t = Trait(conn)
    f = Family(conn)
    p = Profile(conn)
    m = MachineHandler(conn)
    de = DefaultEnvironment(conn)
    
