import os
import subprocess

from useless.base.util import str2list
from useless.base.path import path

from paella.base import PaellaConfig
from paella.base.template import TemplatedEnvironment

from paella.db import DefaultEnvironment
from paella.db.base import get_suite
from paella.db.trait import Trait
from paella.db.trait.relations.parent import TraitParent
from paella.db.family import Family
from paella.db.profile import Profile
from paella.db.profile.main import ProfileEnvironment
from paella.db.machine import MachineHandler


from base import InstallError, InstallerConnection, Modules


# Here is a sample of most of the
# environment during a machine install
# this a pre script (bash) output of env
# These should be only the variables
# tha paella has set.

# PAELLA_TARGET=/tmp/target
# PAELLA_MACHINE=testmachine
# PAELLA_TRAIT=base
# PAELLA_PROFILE=default
# DEBIAN_FRONTEND=noninteractive
# PAELLA_LOGFILE=/paellalog/paella-install-testmachine.log

from base import BaseInstaller
from chroot import ChrootInstaller
from machine import MachineInstaller

#######################
# these installers are a mess
# I don't know what to do with
# them.  I want one of these to
# be the installer attribute of the
# InstallerTools class, but it will
# depend on if the PAELLA_MACHINE
# variable is set or not.
# To start with, I'll use the existence
# of the PAELLA_TRAIT to determine
# this, as the ChrootInstaller will
# be all that's needed on all of the
# trait scripts.  If it's a machine type
# script that is being used, the installer
# should be the MachineInstaller.
#######################

class ToolKitMachineInstaller(MachineInstaller):
    def __init__(self, conn):
        MachineInstaller.__init__(self, conn)
        self.type = 'machine'


class ToolKitChrootInstaller(ChrootInstaller):
    def __init__(self, conn):
        ChrootInstaller.__init__(self, conn)
        self.type = 'chroot'

class ToolKitInstaller(BaseInstaller):
    def __init__(self, conn):
        BaseInstaller.__init__(self, conn)
        

#######################
#######################

class ToolkitDatabase(object):
    def __init__(self, conn):
        self.conn = conn
        self.profile = Profile(self.conn)
        self.family = Family(self.conn)
        self.suite = None
        self.trait = None
        self.machine = MachineHandler(self.conn)
        
    def set_profile(self, profile):
        self.profile.set_profile(profile)
        self.suite = self.profile.current.suite
        self.trait = Trait(self.conn, self.suite)
        
    def set_trait(self, trait):
        self.trait.set_trait(trait)

    def set_machine(self, machine):
        self.machine.set_machine(machine)
        profile = self.machine.get_profile()
        self.set_profile(profile)
        if os.environ.has_key('PAELLA_TRAIT'):
            self.set_trait(os.environ['PAELLA_TRAIT'])
        
        
    def env(self):
        env = TemplatedEnvironment()
        if self.trait.current_trait is not None:
            env.update(self.trait._parents.Environment())
        env.update(self.profile.get_family_data())
        env.update(self.profile.get_profile_data())
        if self.machine.current_machine is not None:
            env.update(self.machine.get_machine_data())
        return env

# here is an exception that will
# be raised when commands that
# are run with subprocess.call
# return non-zero
class CmdLineError(RuntimeError):
    pass

class InstallerTools(object):
    """This is a class that's meant to be called
    in the installer scripts.  It's meant to be
    instantiated as it ->  it = InstallerTools() .
    This class is here to reduce the amount of
    boilerplate code that many of the python
    scripts would require.  A similar file of
    functions for bash would be nice, but there
    is none at the moment.
    """

    def __init__(self):
        object.__init__(self)
        self.cfg = PaellaConfig()
        self.conn = InstallerConnection()
        self.profile = os.environ['PAELLA_PROFILE']
        self.target = path(os.environ['PAELLA_TARGET'])
        self.machine = None
        self.trait = None
        self.suite = get_suite(self.conn, self.profile)
        # we add this here as a convenience
        # we need to think about using check_call
        # instead of call for subprocess (just found
        # out about it)
        self.CmdLineError = CmdLineError

        # another convenience for using
        # pipes in subprocess calls
        self.PIPE = subprocess.PIPE
        
        self.db = ToolkitDatabase(self.conn)
        self.db.set_profile(self.profile)
        self.traits = self.db.profile.make_traitlist()

        # we need better family attributes
        # for both profile families and machine families
        profile_families = self.db.profile.get_families()
        self.profile_families = list(self.db.family.get_related_families(profile_families))
        self.default = DefaultEnvironment(self.conn)

        # we should really use __getattr__ to raise a
        # warning when the families attribute is being
        # accessed so that we can be notified when there
        # are scripts that use it.
        self.families = self.profile_families
        
        if os.environ.has_key('PAELLA_MACHINE'):
            self.machine = os.environ['PAELLA_MACHINE']
            self.db.set_machine(self.machine)
            
        # we need to make an installer to do
        # some of the installer functions.
        self.installer = None

        if os.environ.has_key('PAELLA_TRAIT'):
            self.set_trait(os.environ['PAELLA_TRAIT'])
            
            

    # this needs updating for machine type data
    def env(self):
        return self.db.env()

    def set_trait(self, trait):
        self.trait = trait
        self.db.set_trait(trait)

    def get(self, key):
        env = self.env()
        return env.dereference(key)

    def run(self, cmd):
        retval = subprocess.call(cmd)
        if retval:
            shell_cmd = ' '.join(cmd)
            raise CmdLineError, "Executing: %s , returned %d" % (shell_cmd, retval)
        return retval
    

    def proc(self, cmd, stdin=None, stdout=None, stderr=None):
        proc = subprocess.Popen(cmd, stdin=stdin, stdout=stdout,
                                stderr=stderr)
        return proc

    def _chroot_cmd(self, cmd):
        return ['chroot', str(self.target)] + cmd
    
    def chroot_proc(self, cmd, stdin=None, stdout=None, stderr=None):
        cmd = self._chroot_cmd(cmd)
        return self.proc(cmd, stdin=stdin, stdout=stdout, stderr=stderr)
    
    
    def chroot(self, cmd):
        cmd = self._chroot_cmd(cmd)
        return self.run(cmd)
    
    def set_machine(self, machine):
        self.machine = machine
        self.db.set_machine(machine)
        self.profile = self.db.profile.current.profile
        
        
if __name__ == '__main__':
    from paella.db import PaellaConnection
    conn = PaellaConnection()
    #tp = TraitParent(conn, 'gunny')
    os.environ['PAELLA_PROFILE'] = 'ztest'
    os.environ['PAELLA_TARGET'] = 'nowhere'
    os.environ['PAELLA_LOGFILE'] = 'mylog'
    it = InstallerTools()
    it.set_trait('base')
    
