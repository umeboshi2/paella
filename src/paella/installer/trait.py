import os
from os.path import join, dirname, isfile, isdir
import subprocess

from useless.base.util import makepaths

from paella.debian.debconf import copy_configdb

from paella.db.trait.relations.package import TraitPackage
from paella.db.trait.relations.template import TraitTemplate
from paella.db.trait.relations.script import TraitScript

from base import InstallError
from base import CurrentEnvironment


from util.misc import remove_debs
from util.base import make_script

INGDICT = {
    'install' : 'installing',
    'remove' : 'removing',
    'configure' : 'configuring',
    'config' : 'configuring',
    'reconfig' : 'reconfiguring'
    }

DEFAULT_PROCESSES = ['pre', 'remove', 'install',
                     'templates', 'config', 'chroot', 'reconfig', 'post']

# ------------------------------------------------------------
# new code using BaseProcessor starts here
# ------------------------------------------------------------
from useless.base.path import path
from base import BaseInstaller
from base import runlog

class InstallDebconfError(StandardError):
    pass

class RemoveDebsError(OSError):
    pass

# this class is a preliminary outline for now
class TraitInstallerHelper(object):
    def __init__(self, conn, suite, target):
        # target should already be a path object
        self.target = path(target)
        self.trait = None
        
        # setup relation objects
        self.traitpackage = TraitPackage(conn, suite)
        self.traittemplate = TraitTemplate(conn, suite)
        self.traitscripts = TraitScript(conn, suite)

        # setup empty variable containers
        self.profiledata = {}
        self.mtypedata = {}
        self.familydata = {}

    def set_trait(self, trait):
        self.traitpackage.set_trait(trait)
        self.traittemplate.set_trait(trait)
        self.traitscripts.set_trait(trait)
        self.trait = trait
        self.packages = self.traitpackage.packages()
        self.templates = self.traittemplate.templates()
        os.environ['PAELLA_TRAIT'] = trait
        #self.log.info('trait set to %s' % trait)

    # helper to run commands in a chroot on the target
    def chroot(self, command, failure_suppressed=False):
        cmd = 'chroot %s %s' % (self.target, command)
        return runlog(cmd, failure_suppressed=failure_suppressed)
        
    def remove_packages(self, packages):
        if packages:
            packages_arg = ' '.join(packages)
            command = 'apt-get -y remove %s' % packages_arg
            self.chroot(command)
        else:
            self.log.info('No packages to remove')
        
    def install_packages(self, packages, unauthenticated=False):
        if packages:
            packages_arg = ' '.join(packages)
            opts = ''
            if unauthenticated:
                opts = '--allow-unauthenticated'
            command = 'apt-get -y %s install %s' % (opts, packages_arg)
            stmt = 'install command for trait %s is:  %s' % (self.trait, command)
            self.log.info(stmt)
            self.chroot(command)
        else:
            self.log.info('No packages to install')
            
    def remove_cached_debs(self):
        archives = self.target / 'var/cache/apt/archives'
        partial = archives / 'partial'
        debs = archives.listdir('*.deb')
        pdebs = partial.listdir('*.deb')
        all_debs = debs + pdebs
        for deb in all_debs:
            deb.remove()
            if deb.exists():
                raise RemoveDebsError, 'Failed to remove %s' % deb
            
    # order of updates is important here
    def _update_templatedata(self):
        self.traittemplate.template.update(self.familydata)
        self.traittemplate.template.update(self.mtypedata)
        self.traittemplate.template.update(self.profiledata)
        
    def _make_template_common(self, template, tmpl):
        sub = self.traittemplate.template.sub()
        if tmpl != sub:
            self.log.info('template %s subbed' % (template.template))
        return sub

    def make_template(self, template):
        self.traittemplate.set_template(template.template)
        tmpl = self.traittemplate.template.template
        self._update_templatedata()
        return self._make_template_common(template, tmpl)
        

    def make_template_with_data(self, template, data):
        self.traittemplate.set_template(template.template)
        tmpl = self.traittemplate.template.template
        self.traittemplate.template.update(data)
        return self._make_template_common(template, tmpl)

    # the template argument is a template row
    # in retrospect the template column should've  been 'filename'
    def install_template(self, template, text):
        tname = template.template
        target_filename = self.target / tname
        self.log.info('target template %s' % target_filename)
        makepaths(target_filename.dirname())
        if target_filename.isfile():
            backup_filename = self.target / path('root/paella') / tname
            if not backup_filename.isfile():
                makepaths(backup_filename.dirname())
                target_filename.copy(backup_filename)
                self.log.info('template %s backed up' % tname)
            else:
                msg = 'overwriting previously installed template %s' % tname
                self.log.info(msg)
        else:
            self.log.info('installing NEW template %s' % tname)
        target_filename.write_bytes(text)

        mode = template.mode
        # a simple attempt to insure mode is a valid octal string
        # this is one of the very rare places eval is used
        # there are a few strings with 8's and 9's that will pass
        # the if statement, but the eval will raise SyntaxError then.
        # If the mode is unusable the install will fail at this point.
        if mode[0] == '0' and len(mode) <= 7 and mode.isdigit():
            mode = eval(mode)
            target_filename.chmod(mode)
        else:
            raise InstallError, 'bad mode %s, please use octal prefixed by 0' % mode
        
        own = ':'.join([template.owner, template.grp_owner])
        command = 'chown %s %s' % (own, path('/') / template.template)
        # This command is run in a chroot to make the correct uid, gid
        self.chroot(command)

    def _check_debconf_destroyed(self, config_path):
        if isfile(config_path):
            self.log.warn('%s is not supposed to be there' % config_path)
            raise InstallDebconfError, '%s is not supposed to be there' % config_path

    # here template is the template row
    def install_debconf_template(self, template):
        trait = self.trait
        self.log.info('Installing debconf for %s' % trait)
        self.traittemplate.set_template(template.template)
        tmpl = self.traittemplate.template.template
        self._update_templatedata()
        sub = self.traittemplate.template.sub()
        if tmpl == sub:
            msg = 'static debconf, no substitutions for trait %s' % trait
            self.log.info(msg)
        else:
            self.log.info('templated debconf for trait %s' % trait)
        config_path = self.target / 'tmp/paella_debconf'
        self._check_debconf_destroyed(config_path)
        config_path.write_bytes(sub + '\n')
        target_path = self.target / 'var/cache/debconf/config.dat'
        self.log.info('debconf config is %s %s' % (config_path, target_path))
        copy_configdb(config_path, target_path)
        os.remove(config_path)
        self._check_debconf_destroyed(config_path)
        
    def reconfigure_debconf(self, packages):
        self.log.info('running reconfigure')
        os.environ['DEBIAN_FRONTEND'] = 'noninteractive'
        for package in packages:
            self.log.info('RECONFIGURING %s' % package)
            self.chroot('dpkg-reconfigure -plow %s' % package)
        
        
    def make_script(self, procname):
        script = self.traitscripts.get(procname)
        if script is not None:
            # special handling for the chroot script to ensure
            # it's run in the target chroot
            if procname == 'chroot':
                tmpscript = make_script(procname, script, self.target, execpath=True)
                return 'chroot %s %s' % (self.target, tmpscript)
            else:
                return make_script(procname, script, self.target, execpath=False)
        else:
            return None
        

class TraitInstaller(BaseInstaller):
    def __init__(self, parent):
        BaseInstaller.__init__(self, parent.conn)
        self.target = parent.target
        self.suite = parent.suite
        if False:
            # setup logfile
            if hasattr(parent, 'log'):
                self.log = parent.log
                self.log.info('trait installer initialized')
            else:
                raise RuntimeError, 'No logfile for parent defined'
            
        if hasattr(parent, 'mainlog'):
            self.mainlog = parent.mainlog
            name = self.__class__.__name__
            self.mainlog.add_logger(name)
            self.log = self.mainlog.loggers[name]
        # setup process list
        self._processes = DEFAULT_PROCESSES
        if self.defenv.has_option('installer', 'trait_processes'):
            self._processes = self.defenv.get_list('trait_processes', 'installer')
            
        # setup process map
        # pre and post here are not the same as in the BaseProcessor
        # For example, if a script exists for for pre, it works like this:
        #   self.pre_process()
        #   self.run_process_script(pre)
        #   self.post_process()
        # pre, chroot, config, and post are not mapped
        # as they are scripts only
        self._process_map = dict(remove=self.run_process_remove,
                                 install=self.run_process_install,
                                 templates=self.run_process_templates,
                                 reconfig=self.run_process_reconfig,
                                 )

        # init helper to do the work
        self.helper = TraitInstallerHelper(self.conn, self.suite, self.target)
        # pass the log object to the helper
        self.helper.log = self.log

    def set_trait(self, trait):
        self.helper.set_trait(trait)
        self.current_trait = trait
        self.log.info('trait set to %s' % trait)

    def run_process_remove(self):
        packages = [p.package for p in self.helper.packages if p.action == 'remove']
        self.helper.remove_packages(packages)

    def run_process_install(self):
        packages = [p.package for p in self.helper.packages if p.action == 'install']
        unauthenticated = False
        if self.defenv.getboolean('installer', 'allow_unauthenticated_packages'):
            unauthenticated = True
        self.helper.install_packages(packages, unauthenticated=unauthenticated)
        if not self.defenv.getboolean('installer', 'keep_installed_packages'):
            self.helper.remove_cached_debs()
        else:
            self.log.info('keeping packages for %s' % self.helper.trait)
            
    def run_process_templates(self):
        templates = self.helper.templates
        num = len(templates)
        stmt = 'in run_process_templates, there are %d templates' % num
        stmt = '%s for trait %s' % (stmt, self.helper.trait)
        self.log.info(stmt)
        for t in templates:
            if t.template == 'var/cache/debconf/config.dat':
                self.log.info('Installing Debconf template ...')
                self.helper.install_debconf_template(t)
            else:
                text = self.helper.make_template(t)
                self.helper.install_template(t, text)
            # a hacky way to configure debconf
            if t.template == 'root/paella-debconf.sh':
                self.log.info('Running paella-debconf.sh script ...')
                retval = self.helper.chroot('/root/paella-debconf.sh', failure_suppressed=True)
                # sometimes this script returns 128 and can't be reproduced reliably
                # so we try running it again, until we have no 128 returned
                if retval == 128:
                    count = 0
                    while retval == 128:
                        count += 1
                        if count < 20:
                            self.log.info('/root/paella-debconf.sh returned 128, running again')
                            # this time we will fail on 128
                            retval = self.helper.chroot('/root/paella-debconf.sh',
                                                        failure_suppressed=True)
                        else:
                            raise InstallDebconfError, 'Too many attempts to run debconf script'
                elif retval and retval != 128:
                    msg = "problem running debconf script, returned %d" % retval
                    raise InstallDebconfError, msg
                # rename script
                filename = self.target / 'root/paella-debconf.sh'
                newname = self.target / 'root/%s-paella-debconf.sh' % self.helper.trait
                filename.rename(newname)
                
    def run_process_reconfig(self):
        packages = [p.package for p in self.helper.packages if p.action == 'reconfig']
        self.helper.reconfigure_debconf(packages)

    def make_script(self, procname):
        return self.helper.make_script(procname)


# ------------------------------------------------------------
# new code using BaseProcessor stops here
# ------------------------------------------------------------

