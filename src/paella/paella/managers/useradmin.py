import logging
from ConfigParser import ConfigParser
from StringIO import StringIO
from sqlalchemy.orm.exc import NoResultFound
import transaction


from paella.security import encrypt_password

from paella.models.usergroup import User, Group, Password
from paella.models.usergroup import UserGroup, UserConfig

log = logging.getLogger(__name__)


class UserManager(object):
    def __init__(self, session):
        self.session = session
        
    def user_query(self):
        return self.session.query(User)
    query = user_query
    
    def group_query(self):
        return self.session.query(Group)

    def get_user(self, id):
        return self.user_query().get(id)

    def get_group(self, id):
        return self.group_query().get(id)
        
    def add_user(self, name, password):
        with transaction.manager:
            user = User(name)
            self.session.add(user)
        user = self.session.merge(user)
        self.set_password(user.id, password)
        self.Make_default_config(user.id)
        return user
    

    def set_password(self, user_id, password):
        q = self.session.query(Password).filter_by(user_id=user_id)
        encrypted = encrypt_password(password)
        with transaction.manager:
            try:
                p = q.one()
            except NoResultFound:
                p = Password(user_id, encrypted)
            p.password = encrypted
            self.session.add(p)
            
    def delete_user(self, id):
        with transaction.manager:
            cfg = self.session.query(UserConfig).get(id)
            if cfg is not None:
                self.session.delete(cfg)
            p = self.session.query(Password).get(id)
            if p is not None:
                self.session.delete(p)
            user = self.session.query(User).get(id)
            if user is not None:
                self.session.delete(user)

    def add_user_to_group(self, uid, gid):
        with transaction.manager:
            ug = UserGroup(gid, uid)
            self.session.add(ug)
            
    def remove_user_from_group(self, uid, gid):
        with transaction.manager:
            q = self.session.query(UserGroup)
            ug = q.get((gid, uid))
            self.session.delete(ug)

    def list_groups_for_user(self, uid):
        q = self.session.query(Group, UserGroup)
        q = q.filter(UserGroup.group_id == Group.id)
        q = q.filter(UserGroup.user_id == uid)
        return [r[0] for r in q.all()]

    def list_members_of_group(self, gid):
        q = self.session.query(User, UserGroup)
        q = q.filter(UserGroup.group_id == gid)
        q = q.filter(UserGroup.user_id == User.id)
        return [r[0] for r in q.all()]
        
    def add_group(self, name):
        with transaction.manager:
            g = Group(name)
            self.session.add(g)
        return self.session.merge(g)
    
    def delete_group(self, id):
        with transaction.manager:
            g = self.get_group(id)
            if g is not None:
                self.session.delete(g)
                
    def list_groups(self):
        return self.group_query().all()

    
    def Make_default_config(self, user_id):
        main = dict(sms_email_address='') 
        phonecall_views = dict(received='agendaDay', assigned='agendaWeek',
                               delegated='agendaWeek', unread='agendaWeek',
                               pending='agendaWeek', closed='month')
        c = ConfigParser()
        c.add_section('main')
        for option in main:
            c.set('main', option, main[option])
        c.add_section('phonecall_views')
        for option in phonecall_views:
            c.set('phonecall_views', option, phonecall_views[option])
        cfg = StringIO()
        c.write(cfg)
        cfg.seek(0)
        text = cfg.read()
        with transaction.manager:
            config = UserConfig(user_id, text)
            self.session.add(config)

