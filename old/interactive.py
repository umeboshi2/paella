import os, sys

from useless.base.path import path

from paella.base import PaellaConfig
from paella.db import PaellaConnection
from paella.db.trait import Trait
from paella.db.family import Family
from paella.db.profile import Profile
from paella.db.machine import MachineHandler
from paella.db.installer import InstallerManager

from paella.db import DefaultEnvironment

from paella.installer.toolkit import InstallerTools

if __name__ == '__main__':
    cfg = PaellaConfig()
    conn = PaellaConnection()
    suite = 'bootstrap'
    t = Trait(conn, suite)
    f = Family(conn)
    p = Profile(conn)
    m = MachineHandler(conn)
    de = DefaultEnvironment(conn)
    im = InstallerManager(conn)

    #os.environ['PAELLA_MACHINE'] = 'testmachine'
    os.environ['PAELLA_PROFILE'] = 'default'
    os.environ['PAELLA_TARGET'] = path('/foo/bar')
    it = InstallerTools()
    
