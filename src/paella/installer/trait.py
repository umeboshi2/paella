import os
from os.path import join, dirname, isfile, isdir

from useless.base import Error
from useless.base.util import makepaths

from paella.debian.debconf import copy_configdb
from paella.db.trait.relations import TraitPackage, TraitTemplate
from paella.db.trait.relations import TraitScript

from base import Installer, InstallError

INGDICT = {
    'install' : 'installing',
    'remove' : 'removing',
    'configure' : 'configuring'
    }

class TraitInstaller(Installer):
    def __init__(self, conn, suite, cfg):
        Installer.__init__(self, conn, cfg=cfg)
        self.traitpackage = TraitPackage(conn, suite)
        self.traittemplate = TraitTemplate(conn, suite)
        self.traitscripts = TraitScript(conn, suite)
        self.profiledata = {}
        self.familydata = {}
        
    def set_trait(self, trait):
        self.traitpackage.set_trait(trait)
        self.traittemplate.set_trait(trait)
        self.traitscripts.set_trait(trait)
        self._current_trait_ = trait
        self.log.info('trait set to %s' % self._current_trait_)

    def process(self):
        trait = self._current_trait_
        self.log.info('processing trait:  %s' % trait)
        os.environ['PAELLA_TARGET'] = self.target
        os.environ['PAELLA_TRAIT'] = trait
        packages = self.traitpackage.packages()
        templates = self.traittemplate.templates()
        stmt = 'this trait has %d packages and %d templates' % (len(packages), len(templates))
        self.log.info(stmt)

        #start pre script
        self.process_prepost_script('pre', trait)
        
        #remove packages
        self.process_packages(trait, 'remove', packages)

        #install packages
        self.process_packages(trait, 'install', packages, templates)
        
        #configure packages
        self.log.info('processing config for trait %s' % trait)
        script = self._make_script('config')
        if script is None:
            config = [p for p in packages if p.action in ['install', 'config']]
            if len(config):
                self.configure(config, templates)
        else:
            self.process_hooked_action('config', trait)
        self.log.info('config has been processed for trait %s' % trait)
        
        #reconfigure debconf
        self.log.info('processing reconfig for trait %s' % trait)
        script = self._make_script('reconfig')
        if script is None:
            self.reconfigure_debconf()
        else:
            self.process_hooked_action('reconfig', trait)
        self.log.info('reconfig has been processed for trait %s' % trait)
        
        #start post script
        self.process_prepost_script('post', trait)
        
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
        self.log.info('running script %s trait is currently %s' % (script, trait))
        runvalue = self.run(name, script, chroot=chroot)
        os.remove(script)
        self.log.info(info['done'])

    # prepost is either 'pre' or 'post'
    def process_prepost_script(self, prepost, trait):
        self.log.info('processing %s for trait %s' % (prepost, trait))
        script = self._make_script(prepost)
        runvalue = 0
        if script is not None:
            info = dict(start='%s script started' % prepost,
                        done='%s script done' % prepost)
            runvalue = self.runscript(script, '%s-script' % prepost, info)
        else:
            self.log.info('no %s script for trait %s' % (prepost, trait))
        self.log.info('%s has been processed for trait %s' % (prepost, trait))
        if runvalue:
            raise InstallError, 'Error in running %s script for %s' % (prepost, trait)

    def process_hooked_action(self, action, trait):
        self.log.info('%s has been hooked for trait %s' % (action, trait))
        info = dict(start='%s script started' % action,
                    done='%s script done' % action)
        runvalue = self.runscript(script, '%s-script' % action, info)
        if runvalue:
            InstallError, 'hooked action %s failed on trait %s' % (action, trait)
        
    def process_packages(self, trait, action, packages, templates=[]):
        self.log.info('processing %s for trait %s' % (action, trait))
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
            self.process_hooked_action(action, trait)
        self.log.info('%s has been processed for trait %s' % (action, trait))
        
    def remove(self, packages):
        packages = ' '.join([p.package for p in packages])
        command, args = 'apt-get -y remove', packages
        runvalue = self.run('remove', command, args=args, proc=True)
        if runvalue:
            self.log.warn('Problem removing packages %s' % ', '.join(packages))
            
                
    def install(self, packages, templates):
        trait = self._current_trait_
        package_args = ' '.join([p.package for p in packages])
        cmd = 'apt-get -y --force-yes install %s\n' % package_args
        cmd += 'rm /var/cache/apt/archives/*.deb -f'
        stmt = 'install command for %s is %s' % (cmd, trait)
        self.log.info(stmt)
        runvalue = self.run('install', cmd, proc=True, keeprunning=True)
        if runvalue:
            self.log.warn('PROBLEM installing %s' % trait)
            self.log.warn('packages --> %s' % package_args)
            

    def configure(self, packages, templates):
        dpkg_rec = False
        trait = self._current_trait_
        stmt = 'in configure, there are %d templates for trait %s' % (len(templates), trait)
        self.log.info(stmt)
        for p in packages:
            for t in [t for t in templates if t.package == p.package]:
                if t.template == 'var/cache/debconf/config.dat':
                    dpkg_rec = True
                    self.log.info('Installing Debconf template ...')
                    self.install_debconf_template(t)
                else:
                    self.make_template(t)
        if dpkg_rec:
            self.log.info('Reconfiguring %d packages' % len(packages))
            for p in packages:
                cmd = 'dpkg-reconfigure -plow %s' % p.package
                run = self.run('dpkg-recfg', cmd, proc=True, keeprunning=True)
                if run:
                    self.log.info('reconfigure failed on %s' % p.package)
                else:
                    self.log.info('%s reconfigured' % p.package)
        script = self._make_script('chroot', execpath=True)
        if script is not None:
            self.log.info('chroot exists for trait %s' % trait)
            self.run('chroot-script', script)
            if script[0] == '/':
                script = script[1:]
            os.remove(join(self.target, script))
            
    def _make_script(self, name, execpath=False):
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
        self.traittemplate.template.update(self.familydata)
        self.traittemplate.template.update(self.profiledata)
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
        if mode[0] == '0' and len(mode) <= 7 and mode.isdigit():
            mode = eval(mode)
        os.chmod(newpath, mode)
        own = ':'.join([template.owner, template.grp_owner])
        os.system(self.command('chown', "%s '%s'" %(own, join('/', template.template))))

    def install_debconf_template(self, template):
        trait = self._current_trait_
        self.log.info('Installing debconf for %s' % trait)
        self.traittemplate.set_template(template.package, template.template)
        tmpl = self.traittemplate.template.template
        self.traittemplate.template.update(self.profiledata)
        sub = self.traittemplate.template.sub()
        if tmpl == sub:
            self.log.info('static debconf, no substitutions')
            self.log.info('for trait %s ' % trait)
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

    def install_debconf(self):
        raise Error, 'install_debconf is deprecated, use install_debconf_template instead'
    
    def reconfigure_debconf(self):
        raise Error, 'reconfigure_debconf is deprecated'
        
        
