import logging

from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension

from trumpet.models.usergroup import User, Password
from trumpet.security import authn_policy, authz_policy
from trumpet.config import add_static_views

from paella.models.base import Base

log = logging.getLogger(__name__)

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    settings['db.sessionmaker'] = DBSession
    settings['db.usermodel'] = User
    settings['db.password_model'] = Password
    settings['db.usernamefield'] = 'username'
    


    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    root_factory = 'trumpet.resources.RootGroupFactory'
    request_factory = 'trumpet.request.AlchemyRequest'
    
    config = Configurator(settings=settings,
                          root_factory=root_factory,
                          request_factory=request_factory,
                          authentication_policy=authn_policy,
                          authorization_policy=authz_policy)
    includes = ['pyramid_chameleon', 'pyramid_mako', 'pyramid_beaker',
                'cornice',]
    for i in includes:
        config.include(i)

    client_view = 'paella.views.client.ClientView'
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('apps', '/app/{appname}')
    config.add_view(client_view, route_name='home')
    config.add_view(client_view, route_name='apps')
    config.add_view(client_view, name='login')
    config.add_view(client_view, name='logout')
    config.add_view(client_view, name='admin', permission='admin')

    config.add_route('preseed', '/preseed/{uuid}')
    config.add_route('latecmd', '/latecmd/{uuid}')
    config.scan('paella.views.preseed')
    config.scan('paella.views.diskrecipes')
    config.scan('paella.views.main')
    config.scan('paella.views.currentuser')
    config.scan('paella.views.sitetext')
    config.scan('paella.views.useradmin')
    
    
    # static assets
    serve_static_assets = False
    if 'serve_static_assets' in settings and settings['serve_static_assets'].lower() == 'true':
        serve_static_assets = True

    if serve_static_assets:
        add_static_views(config, settings)
        
    #config.scan('paella.views')

    return config.make_wsgi_app()
