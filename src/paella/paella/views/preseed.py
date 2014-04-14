from pyramid.response import Response
from pyramid.view import view_config
from pyramid.renderers import render


@view_config(route_name='preseed',
             renderer='string')
def preseed_view(request):
    name = request.matchdict['name']
    template = 'paella:templates/preseed.mako'
    env = dict(hostname=name)
    content = render(template, env)
    return content


