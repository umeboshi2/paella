import os
import md5, base64

#this needs to go into another module to keep deps clean
#import ldap
#from ldap.ldapobject import SimpleLDAPObject
SimpleLDAPObject = object

ADMIN_CLASSES = ['top', 'organizationalRole', 'simpleSecurityObject']
CONTACT_CLASSES = ['inetOrgPerson']
GROUP_CLASSES = ['top', 'posixGroup']
ORG_CLASSES = ['top', 'dcObject', 'organization']
OU_CLASSES = ['top', 'organizationalUnit']
USER_CLASSES = ['top', 'posixAccount', 'organizationalPerson']

ADMIN_ATTS = ['cn', 'description', 'userPassword']
CONTACT_ATTS = ['cn', 'sn', 'givenName', 'mail']
GROUP_ATTS = ['cn', 'gidNumber', 'description']
ORG_ATTS = ['dc', 'o']
OU_ATTS = ['ou', 'description']
USER_ATTS = ['uid', 'cn', 'uidNumber', 'gidNumber', 'homeDirectory', 'userPassword',
             'loginShell', 'description', 'sn']

def domain2basedn(domain):
    return ','.join(['dc=%s' % p for p in domain.split('.')])

def basedn2domain(basedn):
    return '.'.join([x[3:] for x in basedn.split(',')])

class Dntuple(object):
    def __init__(self, dn, entry=None):
        object.__init__(self)
        self.dn = dn
        self.parts = self.dn.split(',')
        self.entry = entry
        if entry is None:
            self.entry  = {}

    def __repr__(self):
        return str(tuple([self.dn, self.entry]))
    
        
class ldif_template(object):
    def __init__(self, basedn):
        object.__init__(self)
        self.basedn = basedn
        self.oclasses = []
        self.atts = {}
        self.dntuple = None
        self.main = None
        
    def set_dn(self, att, value):
        if att is None and value is None:
            self.dntuple = Dntuple(self.basedn)
        else:
            self.dntuple = Dntuple('%s=%s,%s' % (att, value, self.basedn), {att:value})
            #self.dn = '%s=%s,%s' % (att, value, self.basedn)
            self.dntuple.entry['objectClass'] = self.oclasses
            self.main = att
            self.dntuple.entry[att] = value

    def __str__(self):
        if self.dntuple:
            dn = 'dn: %s' % self.dntuple.dn
            oclines = ['objectClass: %s' % oc for oc in self.dntuple.entry['objectClass']]
            mainline = '%s: %s' % (self.main, self.dntuple.entry[self.main])
            attlines = []
            for  k,v in self.dntuple.entry.items():
                if k != self.main and k!= 'objectClass' and v is not None:
                    attlines.append('%s: %s' % (k, str(v)))
            return '\n'.join([dn] + oclines + [mainline] + attlines)
        else:
            return 'unset ldif_template'

    def set_password(self, password):
        hashed = md5.new(str(password)).digest()
        encoded = base64.encodestring(hashed)
        self.dntuple.entry['userPassword'] = '{MD5}%s' % encoded.strip()

    def set_desc(self, desc):
        self.dntuple.entry['description'] = desc

    def set_uid(self, uid):
        self.dntuple.entry['uidNumber'] = uid
        
    def set_gid(self, gid):
        self.dntuple.entry['gidNumber'] = gid

    def set_home(self, homepath):
        self.dntuple.entry['homeDirectory'] = os.path.join(homepath, self.dntuple.entry['uid'])
        
        
class admin_template(ldif_template):
    def __init__(self, name, basedn):
        ldif_template.__init__(self, basedn)
        self.oclasses = ADMIN_CLASSES
        self.atts = {}.fromkeys(ADMIN_ATTS)
        self.set_dn(ADMIN_ATTS[0], name)
        
class user_template(ldif_template):
    def __init__(self, name, uid, gid, fullname, basedn, ou=None):
        if ou is not None:
            ldif_template.__init__(self, ','.join([ou, basedn]))
        else:
            ldif_template.__init__(self, basedn)            
        self.oclasses = USER_CLASSES
        self.atts = {}.fromkeys(USER_ATTS)
        self.set_dn(USER_ATTS[0], name)
        self.atts['loginShell'] = '/bin/bash'
        self.set_uid(uid)
        self.set_gid(gid)
        self.dntuple.entry['sn'] = fullname
        self.dntuple.entry['cn'] = name
        
class group_template(ldif_template):
    def __init__(self, name, gid, basedn, ou=None):
        if ou is not None:
            ldif_template.__init__(self, ','.join([ou, basedn]))
        else:
            ldif_template.__init__(self, basedn)            
        self.oclasses = GROUP_CLASSES
        self.atts = {}.fromkeys(GROUP_ATTS)
        self.set_dn(GROUP_ATTS[0], name)
        self.set_gid(gid)
        self.set_desc('%s group' % (name.capitalize()))

class ou_template(ldif_template):
    def __init__(self, name, desc, basedn, ou=None):
        if ou is not None:
            ldif_template.__init__(self, ','.join([ou, basedn]))
        else:
            ldif_template.__init__(self, basedn)            
        self.oclasses = OU_CLASSES
        self.atts = {}.fromkeys(OU_ATTS)
        self.set_dn(OU_ATTS[0], name)
        self.set_desc(desc)

class org_template(ldif_template):
    def __init__(self, domain):
        basedn = domain2basedn(domain)
        ldif_template.__init__(self, basedn)
        self.oclasses = ORG_CLASSES
        self.set_dn(basedn)
        
    def set_dn(self, att):
        self.dntuple = Dntuple(self.basedn)
        self.dntuple.entry['objectClass'] = ORG_CLASSES
        domain = basedn2domain(self.basedn)
        self.dntuple.entry['o'] = domain
        self.dntuple.entry['dc'] = domain.split('.')[0]

    def __str__(self):
        if self.dntuple:
            dn = 'dn: %s' % self.dntuple.dn
            oclines = ['objectClass: %s' % oc for oc in self.dntuple.entry['objectClass']]
            items = self.dntuple.entry.items()
            attlines = ['%s: %s' % (k, str(v)) for k,v in items if k != 'objectClass']
            return '\n'.join([dn] + oclines + attlines)
        else:
            return 'unset ldif_template'

class MainLdif(object):
    def __init__(self, domain, admin, nss, main, people, group_ou):
        self.domain = domain
        self.basedn = domain2basedn(domain)
        self.org = org_template(self.domain)
        self.admin = admin_template(admin, self.basedn)
        self.nss = admin_template(nss, self.basedn)
        mdesc = 'The main organizationalUnit for accounts on the system'
        self.main = ou_template(main, mdesc, self.basedn)
        self.people = ou_template(people, 'User accounts',
                                  self.basedn, ou='ou=%s' % main)
        self.group_ou = ou_template(group_ou, 'Group accounts',
                                  self.basedn, ou='ou=%s' % main)
        self.base_dnames = [self.org, self.admin, self.nss, self.main,
                            self.people, self.group_ou]
        self.users = []
        self.groups = []
        self.gmap, self.umap  = {}, {}
        
    def __str__(self):
        dnames = self.base_dnames + self.groups + self.users
        return '\n\n'.join(map(str, dnames))

    def add_group(self, name, gid):
        main = self.main.dntuple.entry[self.main.main]
        grp = self.group_ou.dntuple.entry[self.group_ou.main]
        ou = 'ou=%s,ou=%s' % (grp, main)
        self.groups.append(group_template(name, gid, self.basedn, ou=ou))
        self.gmap[name] = len(self.groups) - 1
        
    def set_nss_password(self, passwd):
        self.nss.set_password(passwd)

    def set_admin_password(self, passwd):
        self.admin.set_password(passwd)

    def add_user(self, user, uid, gid, fullname, passwd):
        main = self.main.dntuple.entry[self.main.main]
        people = self.people.dntuple.entry[self.people.main]
        ou = 'ou=%s,ou=%s' % (people, main)
        u = user_template(user, uid, gid, fullname,
                          self.basedn, ou=ou)
        u.set_password(passwd)
        self.users.append(u)
        self.umap[user] = len(self.users) - 1

    def write(self, path):
        f = file(path, 'w')
        f.write(str(self))
        f.close()
        
def make_main_ldif(env):
    basedn = env['basedn']
    admin = env['admin']
    nss = env['nss']
    main = env['admin_base']
    domain = env['domain']
    ldif = MainLdif(domain, admin, nss, main, 'people', 'groups')
    ldif.admin.set_password(env['adminpw'])
    ldif.nss.set_password(env['nsspw'])
    ldif.add_group('office', 1000)
    ldif.add_group('admin', 1001)
    ldif.add_user('guest', 1000, 1000, 'Guest User', 'guest')
    ldif.users[ldif.umap['guest']].set_home(env['homepath'])
    return ldif


#this will be moved to another module later
class LdapConnection(SimpleLDAPObject):
    def __init__(self, url, basedn, binddn, bindpw, debug=0):
        SimpleLDAPObject.__init__(self, url, trace_level=debug)
        self.url = url
        self.binddn = binddn
        self.basedn = basedn
        self.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
        if not (binddn is None or basedn is None):
            self.simple_bind_s(self.binddn, bindpw)
        else:
            self.simple_bind_s()

if __name__ == '__main__':
    #conn = LdapConnection('ldap://cervantes', 'dc=lamancha', None, None, 1)
    lt = ldif_template('dc=frobozz,dc=gue')
    a = admin_template('nss', 'dc=frobozz,dc=gue')
    u = user_template('umeboshi', 1001, 1000, 'Joseph Rawswon',
                      'dc=frobozz,dc=gue')#, ou='ou=people,ou=mainoffice')
    g = group_template('office', 1000, 'dc=frobozz,dc=gue')
    ou = ou_template('people', 'user accounts', 'dc=frobozz,dc=gue', ou='ou=connoners,ou=mainoffice')
    o = org_template('dc=frobozz,dc=gue')

    base = 'dc=frobozz,dc=gue'
    l = MainLdif('frobozz.gue', 'admin', 'nss', 'moffice', 'peeple', 'gruups')
    
    from paella.profile.base import PaellaConnection
    from paella.profile.profile import TraitParent
    conn = PaellaConnection()
    tp = TraitParent(conn, 'sarge')
    tp.set_trait('ldap_common')
    tenv = tp.Environment()
    keys = ['basedn', 'admin', 'nss', 'admin_base', 'adminpw', 'nsspw']
    env = dict([(k, tenv['ldap_common_%s' % k]) for k in keys])
    env['domain'] = 'frobozz.gue'
    env['homepath'] = '/freespace/nfsroot/dless/home'
    d = make_main_ldif(env)
