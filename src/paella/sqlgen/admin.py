import os

from paella.base import Error
from classes import cj_fields

def _change_access(type, privilege, tables, user):
    tables = cj_fields(tables)
    if type == 'grant':
        return 'GRANT %s on %s to %s' %(privilege, tables, user)
    elif type == 'revoke':
        return 'REVOKE %s on %s from %s' %(privilege, tables, user)
    else:
        raise Error, 'bad command type in _change_access'

def grant_user(privilege, tables, user):
    return _change_access('grant', privilege, tables, user)

def revoke_user(privilege, tables, user):
    return _change_access('revoke', privilege, tables, user)

def grant_group(privilege, tables, group='mygroup'):
    return _change_access('grant', privilege, tables, 'group %s' %group)

def revoke_group(privilege, tables, group='mygroup'):
    return _change_access('revoke', privilege, tables, 'group %s' %group)


def grant_public(tables, privilege='SELECT'):
    return _change_access('grant', privilege, tables, 'PUBLIC')

def revoke_public(tables, privilege='ALL'):
    return _change_access('revoke', privilege, tables, 'PUBLIC')

def readonly_users_rule(user_group, admin_group, tables):
    full_revoke = revoke_public(tables)
    guser = grant_group('select', tables, user_group)
    gadmin = grant_group('ALL', tables, admin_group)
    return [full_revoke, guser, gadmin]

def create_language(name, handler):
    return 'create language %s handler %s' % (name, handler)

def create_user(name, passwd=None, createdb=False,
                createuser=False, groups=None):
    cmd = 'create user %s' % name
    if passwd is not None:
        cmd += " with encrypted password '%s'" % passwd
    else:
        cmd += ' with'
    cdb = 'nocreatedb'
    cu = 'nocreateuser'
    if createdb:
        cdb = 'createdb'
    if createuser:
        cu = 'createuser'
    cmd += ' %s %s' % (cdb, cu)
    if groups is not None:
        cmd += ' in group %s' % ','.join(groups)
    return cmd

def create_schema(name=None, user=None):
    cmd = 'create schema'
    if name is None and user is None:
        user = os.environ['USER']
        cmd += ' authorization %s' % user
    elif name is None and user is not None:
        cmd += ' authorization %s' % user
    elif name is not None and user is None:
        cmd += ' %s' % name
    else:
        cmd += ' %s authorization %s' % (name, user)
    return cmd

    
