import os
from os.path import join, dirname, isfile, isdir

from paella.base import Error
from paella.base.util import makepaths
from paella.debian.debconf import copy_configdb
from paella.profile.trait import TraitPackage, TraitTemplate, TraitDebconf
from paella.profile.trait import TraitScript

from base import Installer

class TraitInstaller(Installer):
    def __init__(self, conn, suite, cfg):
        Installer.__init__(self, conn, cfg=cfg)
        self.traitpackage = TraitPackage(conn, suite)
        self.traittemplate = TraitTemplate(conn, suite)
        self.traitdebconf = TraitDebconf(conn, suite)
        self.traitscripts = TraitScript(conn, suite)
        
    def set_trait(self, trait):
        self.traitpackage.set_trait(trait)
        self.traittemplate.set_trait(trait)
        self.traitdebconf.set_trait(trait)
        self.traitscripts.set_trait(trait)
        self._current_trait_ = trait
        self.log.info('trait set to %s' % self._current_trait_)

    def run(self, name, command, args='', proc=False, chroot=True,
            keeprunning=False):
        tname = 'trait-%s-%s' % (self._current_trait_, name)
        Installer.run(self, tname, command, args=args, proc=proc,
                      chroot=chroot,
                      keeprunning=keeprunning)
        

    def runscript(self, script, name, info, chroot=False):
        self.log.info(info['start'])
        self.run(name, script, chroot=chroot)
        os.remove(script)
        self.log.info(info['done'])
        
    def process(self):
        self.log.info('processing %s' % self._current_trait_)
        os.environ['PAELLA_TARGET'] = self.target
        os.environ['PAELLA_TRAIT'] = self._current_trait_
        packages = self.traitpackage.packages()
        templates = self.traittemplate.templates()

        #start pre script
        script = self._make_script('pre')
        if script is not None:
            info = dict(start='pre script started',
                        done='pre script done')
            self.runscript(script, 'pre-script', info)
            
        #remove packages
        script = self._make_script('remove')
        if script is None:
            remove = [p for p in packages if p.action == 'remove']
            if len(remove):
                self.remove(remove)
        else:
            info = dict(start='remove script started',
                        done='remove script done')
            self.runscript(script, 'remove-script', info)

        #install packages
        script = self._make_script('install')
        if script is None:
            install = [p for p in packages if p.action == 'install']
            if len(install):
                self.install(install, templates)
        else:
            info = dict(start='install script started',
                        done='install script done')
            self.runscript(script, 'install-script', info)
                        
        #configure packages
        script = self._make_script('config')
        if script is None:
            config = [p for p in packages if p.action in ['install', 'config']]
            if len(config):
                self.configure(config, templates)
        else:
            info = dict(start='config script started',
                        done='config script done')
            self.runscript(script, 'config-script', info)
            
        #reconfigure debconf
        script = self._make_script('reconfig')
        if script is None:
            self.reconfigure_debconf()
        else:
            info = dict(start='reconfig script started',
                        done='reconfig script done')
            self.runscript(script, 'reconfig-script', info)

        #start post script
        script = self._make_script('post')
        if script is not None:
            info = dict(start='post script started',
                        done='post script done')
            self.runscript(script, 'post-script', info)
                
    def remove(self, packages):
        packages = ' '.join([p.package for p in packages])
        command, args = 'apt-get -y remove', packages
        self.run('remove', command, args=args, proc=True)
                
    def install(self, packages, templates):
        package_args = ' '.join([p.package for p in packages])
        cmd = 'apt-get -y --force-yes install %s\n' % package_args
        cmd += 'rm /var/cache/apt/archives/*.deb -f'
        #os.system(self.with_proc(cmd))
        run = self.run('install', cmd, proc=True, keeprunning=True)
        if run:
            self.log.warn('PROBLEM installing %s' % self._current_trait_)
            self.log.warn('packages --> %s' % package_args)
            

    def configure(self, packages, templates):
        dpkg_rec = False
        for p in packages:
            for t in [t for t in templates if t.package == p.package]:
                if t.template == 'var/cache/debconf/config.dat':
                    dpkg_rec = True
                    self.log.info('Installing Debconf template ...')
                    self.install_debconf_template(t)
                else:
                    self.make_template(t)
        if dpkg_rec:
            self.log.info('Reconfiguring packages')
            for p in packages:
                cmd = 'dpkg-reconfigure -plow %s' % p.package
                run = self.run('dpkg-recfg', cmd, proc=True, keeprunning=True)
                if run:
                    self.log.info('reconfigure failed on %s' % p.package)
                else:
                    self.log.info('%s reconfigured' % p.package)
        script = self._make_script('chroot', execpath=True)
        if script is not None:
            #os.system(self.command(script))
            self.run('chroot-script', script)
            if script[0] == '/':
                script = script[1:]
            os.remove(join(self.target, script))
            
    def _make_script(self, name, execpath=False):
        script = self.traitscripts.get(name)
        if script is not None:
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
        self.log.info('target template %s' % newpath)
        dir = dirname(newpath)
        if not isdir(dir):
            makepaths(dir)
        if tmpl != sub:
            self.log.info('%s %s subbed' % (template.package, template.template))
        newfile = file(newpath, 'w')
        newfile.write(sub)
        newfile.close()
        mode = template.mode
        if mode[0] == '0' and len(mode) <= 7 and mode.isdigit():
            mode = eval(mode)
        os.chmod(newpath, mode)
        own = ':'.join([template.owner, template.grp_owner])
        os.system(self.command('chown', '%s %s' %(own, join('/', template.template))))

    def install_debconf_template(self, template):
        self.log.info('Installing debconf for %s' % self._current_trait_)
        self.traittemplate.set_template(template.package, template.template)
        tmpl = self.traittemplate.template.template
        self.traittemplate.template.update(self.profiledata)
        sub = self.traittemplate.template.sub()
        if tmpl == sub:
            self.log.info('static debconf, no substitutions')
            self.log.info('for trait %s ' % self._current_trait_)
        config_path = join(self.target, 'tmp/paella_debconf')
        if isfile(config_path):
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
        config = self.traitdebconf.get_config()
        config_path = join(self.target, 'tmp/paella_debconf')
        if isfile(config_path):
            raise Error, '%s is not supposed to be there' % config_path
        debconf = file(config_path, 'w')
        debconf.write(config + '\n')
        debconf.close()
        target_path = join(self.target, 'var/cache/debconf/config.dat')
        self.log.info('debconf config is %s %s' % (config_path, target_path))
        cmd = install_debconf(config_path, target_path)
        command = 'sh -c "%s"' % cmd
        self.log.info(cmd)
        os.system(cmd)
        os.remove(config_path)

    def reconfigure_debconf(self):
        owners = self.traitdebconf.all_owners()
        self.log.info('ALL OWNERS %s' % owners)
        os.environ['DEBIAN_FRONTEND'] = 'noninteractive'
        for owner in owners:
            self.log.info('RECONFIGURING %s' % owner)
            os.system(self.command('dpkg-reconfigure -plow %s' % owner))
        
        
