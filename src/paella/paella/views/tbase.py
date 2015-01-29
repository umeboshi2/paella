import os
from datetime import datetime

import transaction

from mako.template import Template
from mako.exceptions import MakoException
from mako.exceptions import SyntaxException

from sqlalchemy.exc import OperationalError
from sqlalchemy.exc import UnboundExecutionError
from sqlalchemy.orm.exc import NoResultFound

from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.security import authenticated_userid
from pyramid.renderers import render
from pyramid.response import FileResponse
from pyramid.path import AssetResolver



def static_asset_response(request, asset):
    resolver = AssetResolver()
    descriptor = resolver.resolve(asset)
    if not descriptor.exists():
        raise HTTPNotFound(request.url)
    path = descriptor.abspath()
    response = FileResponse(path, request)
    zip_response = False
    for ending in ['.css', '.js', '.coffee', '.html', '.ttf']:
        if path.endswith(ending):
            zip_response = True
    if zip_response:
        response.encode_content()
    for ending in ['.css', '.js']:
        # one day for css and js
        if path.endswith(ending):
            response.cache_expires(3600*24)
            response.cache_control.public = True
    if path.endswith('.ttf'):
        # one year for fonts
        response.cache_expires(3600*24*365)
        response.cache_control.public = True
    return response

class BaseView(object):
    def __init__(self, request):
        self.request = request
    
    def get_app_settings(self):
        return self.request.registry.settings

class BaseUserView(BaseView):
    def get_current_user_id(self):
        "Get the user id quickly without db query"
        if 'user' not in self.request.session:
            return None
        return self.request.session['user'].id

    def get_current_user(self):
        "Get user db object"
        if 'user' not in self.request.session:
            return None
        db = self.request.db
        user_id = self.request.session['user'].id
        return db.query(self.usermodel).get(user_id)


class BaseViewCallable(BaseView):
    def __init__(self, request):
        super(BaseViewCallable, self).__init__(request)
        self.response = None
        self.data = {}
    
    def __call__(self):
        if self.response is not None:
            return self.response
        else:
            return self.data

class BaseUserViewCallable(BaseViewCallable, BaseUserView):
    pass


