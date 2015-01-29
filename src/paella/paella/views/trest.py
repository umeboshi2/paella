# FIXME merge from trumpet
from paella.views.tbase import BaseUserView

class DBResource(BaseUserView):
    def __init__(self, request):
        super(DBResource, self).__init__(request)
        self.db = self.request.db
    
class BaseResource(DBResource):
    def __init__(self, request):
        super(BaseResource, self).__init__(request)
        if not hasattr(self, 'dbmodel'):
            msg = "need to set dbmodel property before __init__"
            raise RuntimeError, msg

    def query(self):
        return self.db.query(self.dbmodel)

    def _get(self, id):
        return self.query().get(id)
    
    def get(self):
        id = int(self.request.matchdict['id'])
        return self._get(id).serialize()
    
class BaseManagementResource(DBResource):
    def __init__(self, request):
        super(BaseManagementResource, self).__init__(request)
        if not hasattr(self, 'mgrclass'):
            msg = "need to set mgrclass property before __init__"
            raise RuntimeError, msg
        self.mgr = self.mgrclass(self.request.db)
        self.limit = 20
        self.max_limit = 100

    
    def serialize_object(self, dbobj):
        return dbobj.serialize()
    
    def get(self):
        id = int(self.request.matchdict['id'])
        return self.serialize_object(self.mgr.get(id))

    def collection_query(self):
        GET = self.request.GET
        q = self.mgr.query()
        return q
    
    def collection_get(self):
        offset = 0
        limit = self.limit
        GET = self.request.GET
        if 'offset' in GET:
            offset = int(GET['offset'])
        if 'limit' in GET:
            limit = int(GET['limit'])
            if limit > self.max_limit:
                limit = self.max_limit
        q = self.collection_query()
        total_count = q.count()
        q = q.offset(offset).limit(limit)
        objects = q.all()
        return dict(total_count=total_count,
                    data=[self.serialize_object(o) for o in objects])
