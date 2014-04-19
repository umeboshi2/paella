from pyramid.response import Response
from pyramid.view import view_config
from pyramid.renderers import render

@view_config(route_name='preseed',
             renderer='string')
def preseed_view(request):
    settings = request.registry.settings
    paella_server_ip = settings['paella_server_ip']
    name = request.matchdict['name']
    template = 'paella:templates/preseed.mako'
    env = dict(hostname=name, machine=name,
               paella_server_ip=paella_server_ip)
    content = render(template, env)
    return content



@view_config(route_name='latecmd',
             renderer='string')
def latecmd_view(request):
    settings = request.registry.settings
    paella_server_ip = settings['paella_server_ip']
    name = request.matchdict['name']
    template = 'paella:templates/configure-salt-netboot.mako'
    env = dict(machine=name, paella_server_ip=paella_server_ip)
    content = render(template, env)
    return content
    
