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
