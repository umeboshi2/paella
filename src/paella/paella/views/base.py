from pyramid.response import Response
from pyramid.view import view_config


from cornice.resource import resource, view

from sqlalchemy.exc import DBAPIError

from paella.models.base import DBSession
from paella.models.main import MyModel

class BaseResource(object):
    def __init__(self, request):
        self.request = request
        self.db = self.request.db
        if not hasattr(self, 'dbmodel'):
            msg = "need to set dbmodel property before __init__"
            raise RuntimeError, msg

    def _query(self):
        return self.db.query(self.dbmodel)

    def _get(self, id):
        return self._query().get(id)
    
    def get(self):
        id = int(self.request.matchdict['id'])
        return self._get(id).serialize()
    
    def get_current_user_id(self):
        "Get the user id quickly without db query"
        raise RuntimeError, "Not implemented yet"
        return self.request.session['user'].id

    def get_current_user(self):
        "Get user db object"
        raise RuntimeError, "Not implemented yet"
        db = self.request.db
        if 'user' in self.request.session:
            user_id = self.request.session['user'].id
            return db.query(User).get(user_id)
        else:
            return None
        
    def get_app_settings(self):
        return self.request.registry.settings


