import os
import logging
from ConfigParser import ConfigParser
from datetime import datetime

from cornice.resource import resource, view

# FIXME merge from trumpet
from paella.views.tbase import BaseUserView
from paella.views.trest import BaseManagementResource

from paella.models.sitecontent import SiteText
from paella.views.base import MAIN_RESOURCE_ROOT
from paella.views.util import make_resource
from paella.managers.wiki import WikiManager


log = logging.getLogger(__name__)

sitetext_path = os.path.join(MAIN_RESOURCE_ROOT, 'sitetext')


def convert_range_to_datetime(start, end):
    "start and end are timestamps"
    start = datetime.fromtimestamp(float(start))
    end = datetime.fromtimestamp(float(end))
    return start, end

@resource(permission='admin', **make_resource(sitetext_path, ident='name'))
class SiteTextResource(BaseManagementResource):
    mgrclass = WikiManager
    def collection_post(self):
        request = self.request
        db = request.db
        name = request.json['name']
        content = request.json['content']
        #type = request.json.get('type', 'tutwiki')
        page = self.mgr.add_page(name, content)
        response = dict(data=page.serialize(), result='success')
        return response

    def collection_get(self):
        return [p.serialize() for p in self.mgr.query()]
    
    
    def put(self):
        request = self.request
        db = request.db
        name = self.request.matchdict['name']
        page = self.mgr.getbyname(name)
        if page is not None:
            content = request.json.get('content')
            page = self.mgr.update_page(page.id, content)
            page = page.serialize()
            response = dict(result='success')
        else:
            response = dict(result='failure')
        response['data'] = page
        return response

    def delete(self):
        raise RuntimeError, "Implement me!!"
        request = self.request
        db = request.db
        id = int(request.matchdict['id'])
        with transaction.manager:
            st = db.query(SiteText).get(id)
            if st is not None:
                db.delete(st)
        return dict(result='success')
    
    def get(self):
        name = self.request.matchdict['name']
        return self.serialize_object(self.mgr.getbyname(name))

    
