import os

from pyramid.renderers import render


# address can be either mac address or
# system uuid.

def pxeconfig_filename(address):
    # force lowercase for filename
    address = address.lower()
    # FIXME
    dirname = '/var/lib/tftpboot/pxelinux.cfg'
    return os.path.join(dirname, address)

def make_pxeconfig(address, machine, settings):
    filename = pxeconfig_filename(address)
    env = dict(machine=machine, uuid=address,
               paella_server_ip=settings['paella_server_ip'])
    template = 'paella:templates/pxeconfig.mako'
    content = render(template, env)
    with file(filename, 'w') as pxeconfig:
        pxeconfig.write(content)

def remove_pxeconfig(address):
    filename = pxeconfig_filename(address)
    os.remove(filename)
    
