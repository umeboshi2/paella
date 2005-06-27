import os

from paella.profile.base import PaellaConnection, PaellaConfig
from paella.profile.trait import Trait
from paella.profile.family import Family
from paella.profile.profile import Profile
from paella.machines.machine import MachineHandler


if __name__ == '__main__':
    cfg = PaellaConfig()
    conn = PaellaConnection()
    t = Trait(conn)
    f = Family(conn)
    p = Profile(conn)
    m = MachineHandler(conn)
    
