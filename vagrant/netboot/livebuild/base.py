#!/usr/bin/env python
import os, sys
import subprocess

from useless.base.path import path
from useless.base.util import md5sum

# You must be root to run this
# Packages required:  live-build, paella-installer, syslinux, wget

# All of these functions assume that the current working
# directory is the live build directory.

def rmdir(dirname):
    return subprocess.call(['rm', '-fr', dirname])

def remove_chroot():
    dirname = path('chroot')
    if dirname.isdir():
        print "chroot/ exists......removing"
        rmdir(str(dirname))
    if dirname.exists():
        raise RuntimeError , "chroot/ not removed correctly."
    
def install_chroot(machine, arch):
    remove_chroot()
    msg = "Using paella to install %s for arch %s into chroot/"
    msg = msg % (machine, arch)
    print msg

    os.environ['PAELLA_ARCH_OVERRIDE'] = arch
    cmd = ['paella-machine-installer', 'install',
           machine, 'chroot']
    #subprocess.call(['env'])
    retval = subprocess.call(cmd)
    if retval:
        msg = "Something bad happened when running %s, returned %d"
        msg = msg % (' '.join(cmd), retval)
        raise RuntimeError , msg
    del os.environ['PAELLA_ARCH_OVERRIDE']

def stored_chroot_filename(machine, arch):
    return path('stored/%s-%s.tar.gz' % (machine, arch))

def backup_chroot(machine, arch, remove=True):
    stored = stored_chroot_filename(machine, arch)
    if not remove and stored.isfile():
        print "%s already exists. skipping backup...."
        return
    if not stored.dirname().isdir():
        stored.dirname().makedirs()
    cmd = ['tar', 'cfz', str(stored), 'chroot']
    subprocess.check_call(cmd)

def restore_chroot(machine, arch, remove_chroot=True):
    stored  = stored_chroot_filename(machine, arch)
    if not stored.isfile():
        raise RuntimeError , "%s doesn't exist." % stored
    dest = path('chroot')
    if dest.isdir():
        if remove_chroot:
            rmdir(str(dest))
        else:
            RuntimeError , "Won't remove chroot/"
    cmd = ['tar', 'xfz', str(stored)]
    subprocess.check_call(cmd)
    
def prepare_chroot(machine, arch, paella_machine):
    stored  = stored_chroot_filename(machine, arch)
    if stored.isfile():
        print "Using previously stored archive, %s" % stored
        restore_chroot(machine, arch, remove_chroot=True)
    else:
        print "Installing new chroot %s(%s)." % (machine, paella_machine)
        install_chroot(paella_machine, arch)
        backup_chroot(machine, arch, remove=False)

    
def prepare_stagedir():
    stagedir = path('.stage')
    if stagedir.isdir():
        print ".stage/ exists...removing"
        rmdir(str(stagedir))
    stagedir.mkdir()
    bootstrap_stage = stagedir / 'bootstrap'
    # touch empty file
    file(bootstrap_stage, 'w')
    

def call_live_build(logname):
    logfile = file(logname, 'w')
    print "live-build progress being logged in %s" % logname
    subprocess.call(['lb', 'build'], stdout=logfile, stderr=logfile)
    finish_statement = "live-build has finished."
    logfile.write('%s\n' % finish_statement)
    logfile.flush()
    logfile.close()
    

def clean_area():
    retval = subprocess.call(['lb', 'clean'])
    if retval:
        msg = "There was a problem running lb clean."
        raise RuntimeError , msg
    

def setup_config(data):
    filenames = ['binary', 'bootstrap', 'chroot']
    configdir = path('config')
    for config in filenames:
        template_basename = '%s.template' % config
        template_filename = configdir / template_basename
        text = template_filename.text()
        contents = text % data
        configfile = configdir / config
        configfile.write_bytes(contents)

def move_files(target, machine, arch):
    target = path(target)
    if not target.isdir():
        target.mkdir()
    tftpbootdir = target / path('tftpboot/%s' % machine)
    if not tftpbootdir.isdir():
        tftpbootdir.makedirs()
    nfsrootdir = target / path('nfsroot/%s' % machine)
    if not nfsrootdir.isdir():
        nfsrootdir.makedirs()
    os.rename('binary', nfsrootdir / arch)
    os.rename('tftpboot', tftpbootdir / arch)
    packages_filename = '%s.%s.packages' % (machine, arch)
    os.rename('binary.packages',
              nfsrootdir / arch / packages_filename)
    print "Removing chroot/"
    cmd = ['rm', '-fr', 'chroot/']
    retval = subprocess.call(cmd)
    if retval:
        raise RuntimeError , "Problem removing chroot/ directory."


def create_config_data(config, machine, arch):
    for option in ['current_arch', 'arch']:
        config.set(machine, option, arch)
    data = dict(config.items(machine))
    flavor_key = 'linux_flavours_%s' % arch
    data['linux_flavours'] = ''
    if config.has_option(machine, flavor_key):
        data['linux_flavours'] = config.get(machine, flavor_key)
    return data

def make_image_common(machine, arch, config, dest, logfile=None):
    data = create_config_data(config, machine, arch)
    setup_config(data)
    clean_area()
    prepare_stagedir()
    prepare_chroot(machine, arch, data['machine'])
    if logfile is None:
        logfile = 'live-build-%s-%s.log' % (machine, arch)
    call_live_build(logfile)
    
def create_all_chroots(config):
    for machine in config.sections():
        for arch in config.get_archs(machine):
            paella_machine = config.get(machine, 'machine')
            clean_area()
            prepare_chroot(machine, arch, paella_machine)
            clean_area()
    

def make_image(imagetype, machine, arch, config, dest, logfile=None):
    config.set(machine, 'binary_images', imagetype)
    make_image_common(machine, arch, config, dest, logfile=logfile)
    

def make_net_image(machine, arch, config, dest, logfile=None):
    make_image('net', machine, arch, config, dest, logfile=logfile)
    
def make_hybrid_image(machine, arch, config, dest, logfile=None):
    make_image('iso-hybrid', machine, arch, config, dest, logfile=logfile)

def make_hdd_image(machine, arch, config, dest, logfile=None):
    make_image('hdd', machine, arch, config, dest, logfile=logfile)
    
    
if __name__ == "__main__":
    from livebuild.TemplateConfig import template_config as config
    cac = create_all_chroots
