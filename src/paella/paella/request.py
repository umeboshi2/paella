from pyramid.request import Request
from pyramid.decorator import reify


class AlchemyRequest(Request):
    @reify
    def db(self):
        maker = self.registry.settings['db.sessionmaker']
        return maker()
