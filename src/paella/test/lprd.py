import os
from os.path import isfile, join, dirname
import tarfile

from paella.base.config import Configuration
from paella.base.defaults import MB
from paella.base.util import makepaths
from paella.base.tarball import make_tarball

from paella.debian.base import RepositorySource
from paella.profile.base import get_suite

from paella.installer.base import InstallerConnection
from paella.installer.bootstrap import debootstrap
from paella.installer.fstab import UmlFstab
from paella.installer.profile import ProfileInstaller

def create_root_filesystem(path, size=100):
    if isfile(path):
        os.remove(path)
    fs = file(path, 'w')
    fs.truncate(size*MB)
    fs.close()

class Option(object):
    def __init__(self, name, value):
        str.__init__(self)
        self.name = name
        self.value = value
        x = True
        y = False
        
    def __repr__(self):
        return '%s=%s' % (self.name, self.value)

    def __str__(self):
        return '%s=%s' % (self.name, self.value)

class Options(object):
    def __init__(self):
        self._dict = {}

    def __setitem__(self, key, value):
        self._dict[key] = Option(key, value)

    def __getitem__(self, key):
        return self._dict[key]

    def __repr__(self):
        return ' '.join(map(str, self._dict.values()))

    def __str__(self):
        return ' '.join(map(str, self._dict.values()))
    
    def items(self):
        return self._dict.values()

    def values(self):
        return [v.value for v in self._dict.values()]

    def keys(self):
        return self._dict.keys()
    
class _Uml(object):
    def __init__(self):
        object.__init__(self)
        self.options = Options()
        self.options['root'] = '/dev/ubd0'
        self.options['mem'] = '128M'
        
    def devfs(self, option='mount'):
        self.options['devfs'] = option
        
    def forward_sound(self):
        self.dsp = '/dev/sound/dsp'
        self.mixer = 'dev/sound/mixer'

    def console(self):
        self.options['con0'] = 'fd:0,fd:1'
        self.options['con'] = 'pty'

    def __repr__(self):
        return 'linux %s' % self.options

    def __str__(self):
        return str(self.__repr__())


class UmlChroot(_Uml):
    def __init__(self, cfg=None):
        _Uml.__init__(self)
        self.devfs()
        self.console()
        if cfg is None:
            cfg = Configuration('umlchroot')
        self.cfg = cfg
        o = self.options
        o['root'] = '/dev/root'
        o['rootflags'] = '/'
        o['rootfstype'] = 'hostfs'
        o['init'] = self.cfg['initscript']
        o['eth0'] = self.cfg['eth0']
        o['python_path'] = self.cfg['python_path']
        o['paellarc'] = self.cfg['paellarc']

    def set_rootimage(self, path):
        self.options['ubd1'] = path
        
    def run_uml(self):
        return os.system(str(self))

    def set_target(self, target='/tmp/target'):
        self.target = target

    def mount_tmp(self):
        os.system('mount  -t tmpfs tmpfs /tmp')

    def mount_target(self):
        makepaths(self.target)
        os.system('mount /dev/ubd/1 %s' %self.target)
        print self.target, 'mounted'

    def backup_target(self, name):
        nfs = ':'.join([self.cfg['nfs_host'], self.cfg['bkuptarball_path']])
        cmd = 'mount %s /mnt -t nfs -o nolock ' %nfs
        print cmd
        os.system(cmd)
        tarcmd = 'bash -c "tar c --exclude ./proc/* -C %s . > /mnt/%s"' % (self.target,
                                                                  name + '.tar')
        os.system(tarcmd)
        os.system('umount /mnt')


    def extract_root_tarball(self, basetarball):
        here = os.getcwd()
        print 'extracting with tar'
        os.chdir(self.target)
        os.system('tar xf %s' %basetarball)
        os.chdir(here)

    
class UmlBootstrapper(UmlChroot):
    def __init__(self, suite, rootimage=None, cfg=None):
        if rootimage is None:
            rootimage = suite + '.base'
        if cfg is None:
            cfg = Configuration('pbootstrap')
        UmlChroot.__init__(self, cfg)
        self.set_rootimage(rootimage)
        o = self.options
        o['paellasuite'] = suite
        o['basetarball'] = self.cfg['basetarball_path']
        
    def bootstrap(self):
        suite = self.options['paellasuite'].value
        os.system('mke2fs /dev/ubd/1')
        self.mount_target()
        section = self.cfg.section
        self.cfg.change('repos')
        mirror = self.cfg['local_http']
        self.cfg.change(section)
        os.system(debootstrap(suite, self.target, mirror))
        fstab = file(join(self.target, 'etc/fstab'), 'w')
        fstab.write(str(UmlFstab()))
        fstab.close()
        rdev = join(self.target, 'dev/ubd')
        for partition in map(str, range(6)):
            os.system('mknod %s b 98 %s' % (rdev + partition, partition))
        archives = 'var/cache/apt/archives'
        os.system('rm %s -fr' % join(self.target, archives, '*.deb'))
        os.system('rm %s -fr' % join(self.target, archives, 'partial', '*.deb'))
        
        
    def copy_modules(self, kernel_version):
        modpath = join(self.target, 'lib/modules')
        umlmodpath = join('/usr/lib/uml/modules', kernel_version)
        os.system('cp -R %s %s' % (umlmodpath, modpath))

    def make_sources_list(self):
        section = self.cfg.section
        self.cfg.change('repos')
        aptdir = join(self.target, 'etc', 'apt')
        makepaths(aptdir)
        sources_list = file(join(aptdir, 'sources.list'), 'w')
        source = RepositorySource()
        source.uri = self.cfg['local_http']
        suite = self.options['paellasuite'].value
        source.suite = suite
        source.set_path()
        sources_list.write(str(source) +'\n')
        source.type = 'deb-src'
        sources_list.write(str(source) +'\n')
        source.type = 'deb'
        if suite == 'woody':
            source.suite = 'woody/non-US'
            sources_list.write(str(source) +'\n')
            source.type = 'deb-src'
            sources_list.write(str(source) +'\n')
        sources_list.close()
        self.cfg.change(section)

    def make_interfaces(self):
        i = file(join(self.target, 'etc/network/interfaces'), 'w')
        i.write('auto lo eth0\n')
        i.write('iface lo inet loopback\n')
        i.write('iface eth0 inet static\n')
        i.write('\taddress %s\n' %self.cfg['eth_addr'])
        i.write('\tnetmask %s\n' %self.cfg['tun_netmask'])
        i.write('\tgateway %s\n' %self.cfg['gateway'])
        i.write('\n\n')
        i.close()
        
    def set_root_passwd(self, rootline):
        p = file(join(self.target, 'etc/passwd'))
        lines = [rootline + '\n']
        for line in p:
            if line[6:] != 'root::':
                lines.append(line)
        p.close()
        p = file(join(self.target, 'etc/passwd'), 'w')
        p.writelines(lines)
        p.close()

class UmlInstaller(UmlChroot):
    def __init__(self, conn, cfg=None):
        self.conn = conn
        UmlChroot.__init__(self, cfg=cfg)

    def set_suite(self, suite):
        self.options['paellasuite'] = suite
        self.installer = ProfileInstaller(self.conn, suite, self.cfg)

    def set_profile(self, profile):
        self.options['paellaprofile'] = profile
        self.set_suite(get_suite(self.conn, profile))
        self.installer.set_profile(profile)

    def set_template_path(self, path=None):
        if path is None:
            path = self.cfg['template_path']
        self.installer.set_template_path(path)

    def process(self):
        self.installer.process()

    def make_base_image(self, path, size=3000, mkfs='mke2fs'):
        suite = self.options['paellasuite'].value
        basepath = join(self.cfg['basetarball_path'], suite + '.base')
        print 'making root filesystem %s' %path
        create_root_filesystem(path, size)
        self.set_rootimage(path)
        
        
    def copy_base_image(self, path):
        suite = self.options['paellasuite'].value
        basepath = join(self.cfg['basetarball_path'], suite + '.base')
        if basepath != path:
            print 'copying %s to %s' % (basepath, path)
            os.system('cp %s %s' %(basepath, path))
        self.set_rootimage(path)
        
    def install_profile(self, profile, path):
        self.set_profile(profile)
        self.make_base_image(path)
        self.run_uml()
        
    def set_target(self, target='/tmp/target'):
        UmlChroot.set_target(self, target)

    def setup_target(self, target='/tmp/target'):
        self.installer.set_target(target)

    def apt_update(self):
        os.system(self.installer.command('apt-get update'))
        
    def extract_base_tarball(self):
        suite = self.options['paellasuite'].value
        basetarball = join(self.cfg['bkuptarball_path'], '%s.base.tar' % suite)
        if False:
            tar = tarfile.open(mode='r|', fileobj=file(basetarball))
            for info in tar:
                if len(info.name) < 5:
                    print 'extracting', info.name
                tar.extract(info, self.target)
            tar.close()
        else:
            here = os.getcwd()
            print 'extracting with tar'
            os.chdir(self.target)
            os.system('tar xf %s' %basetarball)
            os.chdir(here)

    def mkrootfs(self):
        os.system('mke2fs /dev/ubd/1')

        
def make_base_filesystem(suite, name, cfg=None, size=3000, mkfs='mke2fs'):
    if cfg is None:
        cfg = Configuration('pbootstrap')
    path = join(cfg['basetarball_path'], name)
    makepaths(dirname(path))
    create_root_filesystem(path, 3000)
    uml = UmlBootstrapper(suite, path)
    uml.run_uml()
    
def make_bases():
    for s in ['woody', 'sarge', 'sid']:
        make_base_filesystem(s, s + '.base')








class UmlLeopard(UmlBootstrapper):
    def __init__(self, rootimage=None, cfg=None):
        if rootimage is None:
            rootimage = 'leopard_root'
        UmlBootstrapper.__init__(self, 'leopard', rootimage, cfg)

        








if __name__ == '__main__':
    u = UmlBootstrapper('sid')
    crf = create_root_filesystem
    cfg = Configuration('umlleopard')
    basepath = cfg['basetarball_path']
    conn = InstallerConnection(cfg)
    u = UmlInstaller(conn, cfg)
    path = cfg['rootimage_path']
    ul = UmlLeopard('tmp/leopard', cfg)
    ul.options['root_tarball'] = join(os.getcwd(), 'leopard.tar')
    
