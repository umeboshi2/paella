from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from paella.models.base import (
    DBSession,
    Base,
    )


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    request_factory = 'paella.request.AlchemyRequest'
    
    config = Configurator(settings=settings,
                          request_factory=request_factory,
                          )
    config.include('pyramid_chameleon')
    config.include('pyramid_mako')
    config.include('cornice')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.scan()
    return config.make_wsgi_app()
