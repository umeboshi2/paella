import os

from pyramid.renderers import render


def pxeconfig_filename(address):
    dirname = '/var/lib/tftpboot/pxelinux.cfg'
    return os.path.join(dirname, address)


def make_pxeconfig(address, machine):
    filename = pxeconfig_filename(address)
    env = dict(machine=machine)
    template = 'paella:templates/pxeconfig.mako'
    content = render(template, env)
    with file(filename, 'w') as pxeconfig:
        pxeconfig.write(content)


def remove_pxeconfig(address):
    filename = pxeconfig_filename(address)
    os.remove(filename)
    
