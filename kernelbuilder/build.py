import os, sys
from os.path import join, isfile, isdir
from time import sleep
import commands

from paella.base import Error
from paella.base.config import Configuration

config = Configuration(files='./kernels.conf')
here = os.getcwd()

def get_all_kernels():
    return config.get_list('allkernels', 'DEFAULT')

def get_version(dir=here):
    changelog = join(dir, 'debian/changelog')
    pipeline = "head -n1 %s | gawk '{print $2}' " % changelog
    pipeline += " | cut -f2 -d\( | cut -f1 -d\)"
    command = 'bash -c "%s"' % pipeline
    return commands.getoutput(command)

def commalist(a_list):
    return ','.join(a_list)

def kernel_name(flavor):
    config.change(flavor)
    kver = config['kver']
    kname = config['kname']
    kernel = kname + kver
    return kernel

def unpack_ksrc(flavor):
    config.change(flavor)
    kernel = kernel_name(flavor)
    tarball = join(config['ksrc_dir'], '%s.tar.bz2' % kernel)
    if not isfile('stamp_unpack_%s' % kernel):
        print 'extracting', kernel
        os.system('bash -c "bzip2 -cd %s | tar x"' % tarball)
        #os.system('cp debian/control %s/debian' % kernel)
        #os.system('cp debian/changelog %s/debian' % kernel)
        #os.system('cp debian/copyright %s/debian' % kernel)
        os.system('touch stamp_unpack_%s' %kernel)
    else:
        print 'kernel %s previously unpacked' % config['kver']

def build_dir(flavor):
    config.change(flavor)
    return '%s-%s' % (kernel_name(flavor), flavor)

def remove_build_dir(flavor):
    os.chdir(here)
    config.change(flavor)
    bdir = build_dir(flavor)
    rm = os.system('rm %s -fr' % bdir)
    if rm:
        raise Error, 'problem removing %s' % bdir
    else:
        print bdir, 'removed'


def make_build_dir(flavor):
    pwd = os.getcwd()
    config.change(flavor)
    kernel = kernel_name(flavor)
    os.chdir(here)
    kdir = build_dir(flavor)
    if not isdir(kdir):
        print 'creating build dir for', flavor
        os.system('cp -al %s %s' % (kernel, kdir))
        if os.system('cp kernels/%s %s/.config' % (config['config'], kdir)):
            raise Error, 'problem copying config for %s' % flavor
        print '%s ready for building' % kdir
        
    

def kpkg_command(flavor, command='kernel-image'):
    config.change(flavor)
    patches = config['patches']
    modules = config['modules']
    fullcmd = 'make-kpkg'
    fullcmd += ' --rootcmd %s' % config['rootcmd']
    if config['initrd'] == 'true':
        fullcmd += ' --initrd'
    fullcmd += ' %s ' % config['extra_opts']
    if patches:
        fullcmd += ' --added-patches %s' % patches
    if modules:
        fullcmd += ' --added-modules %s' % modules
    if config['flavor']:
        flavor = config['flavor']
    fullcmd += ' --append-to-version %s' % flavor
    fullcmd += ' --revision %s' % get_version()
    fullcmd += ' %s' % command
    return fullcmd
    
def make_kernel_image(flavor):
    if config['initrd'] == 'true':
        os.environ['INITRD_OK'] = 'true'
    if not isfile('stamp_mkimg_%s' % flavor):
        if isfile('stamp_build_%s' % flavor):
            os.chdir(build_dir(flavor))
            mkimg = os.system(kpkg_command(flavor, 'kernel-image'))
            os.system('bash -c "cat debian/files >> ../debian/files"')
            os.chdir(here)
            if not mkimg:
                os.system('touch stamp_mkimg_%s' % flavor)
                print 'make kernel-image on %s completed' % flavor
            else:
                print 'there was a problem making kernel-image on', flavor
        else:
            raise Error, 'need to build kernel first'

def build_kernel(flavor):
    kernel = kernel_name(flavor)
    if not isdir(kernel):
        unpack_ksrc(flavor)
    while not isfile('stamp_unpack_%s' % kernel):
        print 'waiting for unpack', kernel
        sleep(2)
    if not isfile('stamp_build_%s' %flavor):
        os.environ['CONCURRENCY_LEVEL'] = '30'
        config.change(flavor)
        bdir = build_dir(flavor)
        if config['initrd'] == 'true':
            os.environ['INITRD_OK'] = 'true'
        if not isdir(bdir):
            make_build_dir(flavor)
        os.chdir(bdir)
        cmd = kpkg_command(flavor, 'build')
        build = os.system(cmd)
        os.chdir(here)
        if not build:
            os.system('touch stamp_build_%s' %flavor)
            print 'build done on', flavor
        else:
            print 'there was an error building', flavor

    else:
        print 'build previously completed for', flavor


def package_section(kernel):
    fields = ['package', 'architecture', 'section', 'priority',
              'provides', 'depends', 'suggests', 'description']
    flavor = kernel
    if config.get(kernel, 'flavor'):
        flavor = config.get(kernel, 'flavor')
    section = 'Package: kernel-image-%s%s\n' % (config.get(kernel, 'kver'), flavor)
    for field in fields[1:-1]:
        section += '%s: %s\n' % (field.capitalize(), config.get(kernel, field))
    lines = config.get(kernel, 'description').split('\n')
    section += 'Description: %s' % '\n'.join(lines[:1] + [' %s' % x for x in lines[1:]])
    return section


def build_kernel_image(kernel):
    build_kernel(kernel)
    make_kernel_image(kernel)
    

def unpack_all():
    kernels = get_all_kernels()
    for kernel in kernels:
        unpack_ksrc(kernel)
        make_build_dir(kernel)
        
def build_all():
    kernels = get_all_kernels()
    for kernel in kernels:
        build_kernel(kernel)
        
def make_all_kernel_images():
    kernels = get_all_kernels()
    for kernel in kernels:
        make_kernel_image(kernel)
        
def clean_all():
    kernels = get_all_kernels()
    for kernel in kernels:
        remove_build_dir(kernel)
        os.system('rm stamp_build_%s -f' % kernel)
        os.system('rm stamp_mkimg_%s -f' % kernel)
        os.system('rm %s -fr' % kernel_name(kernel))
        os.system('rm stamp_unpack_%s -f' % kernel_name(kernel))
        
def generate_control_info():
    kernels = get_all_kernels()
    for kernel in kernels:
        section = package_section(kernel)
        control = file('debian/control', 'a')
        control.write(section + '\n\n')
        control.close()
        print 'control file appended for', kernel

        

RUNDICT = {
    'unpack' : unpack_all,
    'build' : build_all,
    'kernel-image' : make_all_kernel_images,
    'clean' : clean_all,
    'configure' : generate_control_info
    }

def run(command):
    RUNDICT[command]()

if __name__ == '__main__':
    #c = make_kpkg_cmd('install', ['skas', 'uml'], ['cloop'], 'roujin')
    #print kpkg_command('roujin', 'build')
    command = sys.argv[1]
    if command == 'make':
        build_kernel_image(sys.argv[2])
    else:
        run(command)
    
