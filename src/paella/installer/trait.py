import os
from os.path import join, dirname, isfile, isdir

from useless.base import Error
from useless.base.util import makepaths

from paella.debian.debconf import copy_configdb
#from paella.db import CurrentEnvironment
from paella.db.trait.relations import TraitPackage, TraitTemplate
from paella.db.trait.relations import TraitScript

from base import Installer, InstallError
from base import CurrentEnvironment
from util import remove_debs, make_script

INGDICT = {
    'install' : 'installing',
    'remove' : 'removing',
    'configure' : 'configuring',
    'config' : 'configuring',
    'reconfig' : 'reconfiguring'
    }

DEFAULT_PROCESSES = ['pre', 'remove', 'install',
                     'templates', 'config', 'chroot', 'reconfig', 'post']

class TraitInstaller(Installer):
    def __init__(self, conn, suite):
        Installer.__init__(self, conn)
        self.traitpackage = TraitPackage(conn, suite)
        self.traittemplate = TraitTemplate(conn, suite)
        self.traitscripts = TraitScript(conn, suite)
        self.profiledata = {}
        self.mtypedata = {}
        self.familydata = {}
        self.trait_processes = DEFAULT_PROCESSES
        if self.defenv.has_option('installer', 'trait_processes'):
            self.trait_processes = self.defenv.get_list('trait_processes', 'installer')
            
        self._process_map = {
            'pre' : self._process_pre,
            'remove' : self._process_remove,
            'install' : self._process_install,
            'templates' : self._process_templates,
            'config' : self._process_config,
            'chroot' : self._process_chroot,
            'reconfig' : self._process_reconfig,
            'post' : self._process_post
            }
        
    def set_trait(self, trait):
        self.traitpackage.set_trait(trait)
        self.traittemplate.set_trait(trait)
        self.traitscripts.set_trait(trait)
        self._current_trait_ = trait
        self.packages = self.traitpackage.packages()
        self.templates = self.traittemplate.templates()
        os.environ['PAELLA_TRAIT'] = trait
        self.log.info('trait set to %s' % self._current_trait_)

    def _info(self):
        return self._current_trait_, self.packages, self.templates
    
    def _process_pre(self):
        self.process_prepost_script('pre', self._current_trait_)

    def _process_remove(self):
        trait, packages, templates = self._info()
        self.process_packages(trait, 'remove', packages)

    def _process_install(self):
        trait, packages, templates = self._info()
        self.process_packages(trait, 'install', packages, templates)

    def _process_config(self):
        trait, packages, templates = self._info()
        script = self._make_script('config')
        if script is None:
            self.log.info('there is no config script for trait %s' % trait)
        else:
            self.process_hooked_action(script, 'config', trait)

    def _process_generic_script(self, action):
        trait, packages, templates = self._info()
        script = self._make_script(action)
        if script is None:
            self.log.info('there is no %s script for trait %s' % (action, trait))
        else:
            self.process_hooked_action(script, action, trait)
        
    def _process_templates(self):
        trait, packages, templates = self._info()
        script = self._make_script('templates')
        if script is None:
            tpackages = [p for p in packages if p.action in ['install', 'config']]
            if len(tpackages) or len(templates):
                self.install_templates(tpackages, templates)
        else:
            self.process_hooked_action(script, 'templates', trait)
        
    def _process_chroot(self):
        trait, packages, templates = self._info()
        script = self._make_script('chroot', execpath=True)
        if script is not None:
            self.log.info('chroot exists for trait %s' % trait)
            self.run('chroot-script', script)
            if script[0] == '/':
                script = script[1:]
            os.remove(join(self.target, script))
        
    def _process_reconfig(self):
        trait, packages, templates = self._info()
        script = self._make_script('reconfig')
        if script is None:
            self.reconfigure_debconf(packages)
        else:
            self.process_hooked_action(script, 'reconfig', trait)
        
    def _process_post(self):
        self.process_prepost_script('post', self._current_trait_)

    def process(self):
        trait, packages, templates = self._info()
        self.log.info('processing trait:  %s' % trait)
        if 'PAELLA_TARGET' not in os.environ.keys():
            self.log.warn('PAELLA_TARGET not set.')
            os.environ['PAELLA_TARGET'] = self.target
        machine = None
        curenv = {}
        if 'PAELLA_MACHINE' in os.environ.keys():
            machine = os.environ['PAELLA_MACHINE']
            curenv = CurrentEnvironment(self.conn, machine)
        if machine is not None:
            self.log.info('processing trait %s on machine %s' % (trait, machine))
        curenv['current_trait'] = trait
        for proc in self.trait_processes:
            self.log.info('processing %s for trait %s' % (proc, trait))
            curenv['current_trait_process'] = proc
            if proc in self._process_map.keys():
                self._process_map[proc]()
            else:
                self._process_generic_script(proc)
            self.log.info('%s has been processed for trait %s' % (proc, trait))
            
    
    def run(self, name, command, args='', proc=False, chroot=True,
            keeprunning=False):
        tname = 'trait-%s-%s' % (self._current_trait_, name)
        self.log.info('running %s' % tname)
        runvalue = Installer.run(self, tname, command, args=args, proc=proc,
                                 chroot=chroot,
                                 keeprunning=keeprunning)
        return runvalue

    def runscript(self, script, name, info, chroot=False):
        self.log.info(info['start'])
        trait = self._current_trait_
        self.log.info('running script %s for trait %s' % (script, trait))
        runvalue = self.run(name, script, chroot=chroot)
        os.remove(script)
        self.log.info(info['done'])

    # prepost is either 'pre' or 'post'
    def process_prepost_script(self, prepost, trait):
        script = self._make_script(prepost)
        runvalue = 0
        if script is not None:
            info = dict(start='%s script started' % prepost,
                        done='%s script done' % prepost)
            runvalue = self.runscript(script, '%s-script' % prepost, info)
        else:
            self.log.info('no %s script for trait %s' % (prepost, trait))
        if runvalue:
            raise InstallError, 'Error in running %s script for %s' % (prepost, trait)

    def process_hooked_action(self, script, action, trait):
        self.log.info('%s has been hooked for trait %s' % (action, trait))
        info = dict(start='%s script started' % action,
                    done='%s script done' % action)
        runvalue = self.runscript(script, '%s-script' % action, info)
        if runvalue:
            InstallError, 'hooked action %s failed on trait %s' % (action, trait)
        
    def process_packages(self, trait, action, packages, templates=[]):
        script = self._make_script(action)
        if script is None:
            affected = [p for p in packages if p.action == action]
            length = len(affected)
            if length:
                ing = INGDICT[action]
                stmt = '%s %d packages for trait %s' % (ing, length, trait)
                self.log.info(stmt)
                if action == 'remove':
                    self.remove(affected)
                elif action == 'install':
                    self.install(affected, templates)
                else:
                    raise InstallError, '%s not implemented in process_packages'
        else:
            self.process_hooked_action(script, action, trait)
        
    def remove(self, packages):
        packages = ' '.join([p.package for p in packages])
        command, args = 'apt-get -y remove', packages
        runvalue = self.run('remove', command, args=args, proc=True)
        if runvalue:
            self.log.warn('Problem removing packages %s' % ', '.join(packages))
            
                
    def install(self, packages, templates):
        trait = self._current_trait_
        package_args = ' '.join([p.package for p in packages])
        cmd = 'apt-get -y --force-yes install %s' % package_args
        stmt = 'install command for %s is %s' % (trait, cmd)
        self.log.info(stmt)
        runvalue = self.run('install', cmd, proc=False, keeprunning=False)
        if runvalue:
            self.log.warn('PROBLEM installing %s' % trait)
            self.log.warn('packages --> %s' % package_args)
            raise InstallError, 'problem installing packages'
        runvalue = remove_debs(self.target)
        if runvalue:
            self.log.warn('PROBLEM removing downloaded debs')
            raise InstallError, 'problem removing downloaded debs'
        
    def install_templates(self, packages, templates):
        trait = self._current_trait_
        num = len(templates)
        stmt = 'in install_templates, there are %d templates for trait %s' % (num, trait)
        self.log.info(stmt)
        if packages:
            print 'ignoring packages', packages
        for t in templates:
            if t.template == 'var/cache/debconf/config.dat':
                self.log.info('Installing Debconf template ...')
                self.install_debconf_template(t)
            else:
                self.make_template(t)
            
    def configure(self, packages, templates):
        trait = self._current_trait_
        stmt = 'in configure, there are %d templates for trait %s' % (len(templates), trait)
        self.log.info(stmt)
        for p in packages:
            for t in [t for t in templates if t.package == p.package]:
                if t.template == 'var/cache/debconf/config.dat':
                    self.log.info('Installing Debconf template ...')
                    self.install_debconf_template(t)
                else:
                    self.make_template(t)
            
    def _make_script(self, name, execpath=False):
        script = self.traitscripts.get(name)
        if script is not None:
            stmt = '%s script exists for trait %s' % (name, self._current_trait_)
            self.log.info(stmt)
            return make_script(name, script, self.target, execpath=execpath)
        else:
            return None
        
    def _make_scriptOrig(self, name, execpath=False):
        script = self.traitscripts.get(name)
        if script is not None:
            stmt = '%s script exists for trait %s' % (name, self._current_trait_)
            self.log.info(stmt)
            exec_path = join('/tmp', name + '-script')
            target_path = join(self.target, 'tmp', name + '-script')
            sfile = file(target_path, 'w')
            sfile.write(script.read())
            sfile.close()
            os.system('chmod 755 %s' % target_path)
            if not execpath:
                return target_path
            else:
                return exec_path
        else:
            return None
        
    def make_template(self, template):
        self.traittemplate.set_template(template.package, template.template)
        tmpl = self.traittemplate.template.template
        self._update_templatedata()
        self._make_template_common(template, tmpl)
        

    def make_template_with_data(self, template, data):
        self.traittemplate.set_template(template.package, template.template)
        tmpl = self.traittemplate.template.template
        self.traittemplate.template.update(data)
        self._make_template_common(template, tmpl)
        
    def _make_template_common(self, template, tmpl):
        sub = self.traittemplate.template.sub()
        newpath = join(self.target, template.template)
        bkuppath = join(self.target, self.paelladir, 'original_files', template.template)
        makepaths(dirname(newpath), dirname(bkuppath))
        self.log.info('target template %s' % newpath)
        if tmpl != sub:
            self.log.info('%s %s subbed' % (template.package, template.template))
        if isfile(newpath):
            if not isfile(bkuppath):
                os.system('mv %s %s' % (newpath, dirname(bkuppath)))
                self.log.info('%s backed up' % template.template)
            else:
                self.log.info('overwriting previously installed template %s' % template.template)
        else:
            self.log.info('installing new template %s' % template.template)
        newfile = file(newpath, 'w')
        newfile.write(sub)
        newfile.close()
        mode = template.mode
        
        # a simple attempt to insure mode is a valid octal string
        # this is one of the very rare places eval is used
        # there are a few strings with 8's and 9's that will pass
        # the if statement, but the eval will raise SyntaxError then.
        # If the mode is unusable the install will fail at this point.
        if mode[0] == '0' and len(mode) <= 7 and mode.isdigit():
            mode = eval(mode)
            os.chmod(newpath, mode)
        else:
            raise InstallError, 'bad mode %s, please use octal prefixed by 0' % mode
        
        own = ':'.join([template.owner, template.grp_owner])
        os.system(self.command('chown', "%s '%s'" %(own, join('/', template.template))))

    def _update_templatedata(self):
        self.traittemplate.template.update(self.familydata)
        self.traittemplate.template.update(self.mtypedata)
        self.traittemplate.template.update(self.profiledata)
        
    def install_debconf_template(self, template):
        trait = self._current_trait_
        self.log.info('Installing debconf for %s' % trait)
        self.traittemplate.set_template(template.package, template.template)
        tmpl = self.traittemplate.template.template
        self._update_templatedata()
        sub = self.traittemplate.template.sub()
        if tmpl == sub:
            self.log.info('static debconf, no substitutions')
            self.log.info('for trait %s ' % trait)
        else:
            self.log.info('templated debconf for trait %s' % trait)
        config_path = join(self.target, 'tmp/paella_debconf')
        if isfile(config_path):
            self.log.warn('%s is not supposed to be there' % config_path)
            raise Error, '%s is not supposed to be there' % config_path
        debconf = file(config_path, 'w')
        debconf.write(sub + '\n')
        debconf.close()
        target_path = join(self.target, 'var/cache/debconf/config.dat')
        self.log.info('debconf config is %s %s' % (config_path, target_path))
        copy_configdb(config_path, target_path)
        os.remove(config_path)

    def set_template_path(self, path):
        self.traittemplate.template.set_path(path)

    def reconfigure_debconf(self, packages):
        self.log.info('running reconfigure')
        reconfig = [p.package for p in packages if p.action == 'reconfig']
        os.environ['DEBIAN_FRONTEND'] = 'noninteractive'
        for package in reconfig:
            self.log.info('RECONFIGURING %s' % package)
            os.system(self.command('dpkg-reconfigure -plow %s' % package))
        
        
