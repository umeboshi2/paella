from pyramid.response import Response
from pyramid.view import view_config
from pyramid.renderers import render


from paella.managers.main import MachineManager

def _installer_view(request, template):
    mgr = MachineManager(request.db)
    settings = request.registry.settings
    paella_server_ip = settings['paella_server_ip']
    uuid = request.matchdict['uuid']
    m = mgr.get_by_uuid(uuid)
    name = m.name
    env = dict(uuid=uuid, hostname=name, machine=name,
               paella_server_ip=paella_server_ip)
    content = render(template, env)
    return content
    

@view_config(route_name='preseed',
             renderer='string')
def preseed_view(request):
    template = 'paella:templates/preseed.mako'
    return _installer_view(request, template)

@view_config(route_name='latecmd',
             renderer='string')
def latecmd_view(request):
    template = 'paella:templates/configure-salt-netboot.mako'
    return _installer_view(request, template)
    
