import os

from sqlalchemy.orm.exc import NoResultFound

from pyramid.security import remember, forget

from trumpet.security import check_password, encrypt_password

from trumpet.models.usergroup import User, Password


class UserContainer(object):
    pass


def check_login_form(request):
    username = request.params['username']
    password = request.params['password']
    dbsession = request.db
    try:
        user = dbsession.query(User).filter_by(username=username).one()
    except NoResultFound:
        return False
    try:
        dbpass = dbsession.query(Password).filter_by(user_id=user.id).one()
    except NoResultFound:
        return False
    authenticated = check_password(dbpass.password, password)
    if authenticated:
        # when we attach the user object to the session
        # we can't use the actual db object without rebinding
        # to the db later, creating excessive traffic.  To
        # mitigate this, an attribute container in the form
        # of the db object is used instead.
        uc = UserContainer()
        uc.username = user.username
        uc.id = user.id
        uc.groups = user.get_groups()
        request.session['user'] = uc
    return authenticated


#@resource(**make_resource(path, ident='name'))
def make_resource(rpath, ident='id', cross_site=True):
    path = os.path.join(rpath, '{%s}' % ident)
    data = dict(collection_path=rpath, path=path)
    if cross_site:
        data['cors_origins'] = ('*',)
    return data

