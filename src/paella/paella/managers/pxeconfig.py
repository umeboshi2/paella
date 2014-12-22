import os
import logging

from pyramid.renderers import render

log = logging.getLogger(__name__)

# uuid is system uuid.

def pxeconfig_filename(uuid):
    # force lowercase for filename
    uuid = uuid.lower()
    # FIXME
    dirname = '/var/lib/tftpboot/pxelinux.cfg'
    return os.path.join(dirname, uuid)

# machine is db object
def make_pxeconfig(machine, settings):
    filename = pxeconfig_filename(machine.uuid)
    env = dict(machine=machine,
               paella_server_ip=settings['paella_server_ip'],
               debconf_debug=settings.get('debconf_debug', ''))
    template = 'paella:templates/pxeconfig.mako'
    content = render(template, env)
    with file(filename, 'w') as pxeconfig:
        pxeconfig.write(content)

def remove_pxeconfig(uuid):
    filename = pxeconfig_filename(uuid)
    os.remove(filename)
    
