import os
from ConfigParser import ConfigParser
from datetime import datetime

from cornice.resource import resource, view
from trumpet.views.rest import BaseResource, BaseManagementResource

from cenotaph.models.usergroup import User, Group, Password
from cenotaph.models.usergroup import UserGroup

from cenotaph.views.util import make_resource as make_base_resource
from cenotaph.views.rest import MAIN_RESOURCE_ROOT
from cenotaph.managers.useradmin import UserManager

rscroot = MAIN_RESOURCE_ROOT


users_path = os.path.join(rscroot, 'users')
groups_path = os.path.join(rscroot, 'groups')
usergroup_path = os.path.join(users_path, '{uid}', 'groups')
groupmember_path = os.path.join(groups_path, '{gid}', 'members')                           
def convert_range_to_datetime(start, end):
    "start and end are timestamps"
    start = datetime.fromtimestamp(float(start))
    end = datetime.fromtimestamp(float(end))
    return start, end

def make_resource(rpath, ident='id', cross_site=True):
    data = make_base_resource(rpath, ident=ident, cross_site=cross_site)
    data['permission'] = 'admin'
    return data



@resource(**make_resource(users_path))
class UserResource(BaseManagementResource):
    dbmodel = User
    mgrclass = UserManager
    def collection_get(self):
        q = self.mgr.user_query()
        return dict(data=[o.serialize() for o in q], result='success')
    
    def collection_post(self):
        name = self.request.json['name']
        password = self.request.json['password']
        obj = self.mgr.add_user(name, password)
        data = dict(obj=obj.serialize(), result='success')
        return data

    def delete(self):
        id = int(self.request.matchdict['id'])
        self.mgr.delete_user(id)
        return dict(result='success')


@resource(**make_resource(groups_path))
class GroupResource(BaseManagementResource):
    dbmodel = Group
    mgrclass = UserManager
    def collection_get(self):
        q = self.mgr.group_query()
        return dict(data=[o.serialize() for o in q])

    def collection_post(self):
        name = self.request.json['name']
        g = self.mgr.add_group(name)
        return dict(obj=g.serialize(), result='success')

    def delete(self):
        id = int(self.request.matchdict['id'])
        self.mgr.delete_group(id)
        return dict(result='success')

@resource(**make_resource(usergroup_path))
class UserGroupResource(BaseManagementResource):
    dbmodel = UserGroup
    mgrclass = UserManager
    def collection_get(self):
        uid = int(self.request.matchdict['uid'])
        groups = self.mgr.list_groups_for_user(uid)
        data = [g.serialize() for g in groups]
        return dict(data=data)

    def collection_post(self):
        gid = self.request.json['id']
        uid = int(self.request.matchdict['id'])
        self.mgr.add_user_to_group(uid, gid)
        return dict(result='success')

    def delete(self):
        uid = int(self.request.matchdict['uid'])
        gid = int(self.request.matchdict['id'])
        self.mgr.remove_user_from_group(uid, gid)
        return dict(result='success')

    def get(self):
        gid = int(self.request.matchdict['id'])
        return dict(data=self.mgr.get_group(gid).serialize())
    
@resource(**make_resource(groupmember_path, ident='uid'))
class GroupMemberResource(BaseManagementResource):
    dbmodel = UserGroup
    mgrclass = UserManager
    def collection_get(self):
        gid = int(self.request.matchdict['gid'])
        users = self.mgr.list_members_of_group(gid)
        data = [u.serialize() for u in users]
        return dict(data=data)

    
