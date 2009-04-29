# -*- mode: python -*-
import sys

from useless.base.path import path

from paella.installer.toolkit import InstallerTools

#################################
def get_all_defined_groups(toolkit):
    it = toolkit
    extra_groups = it.get('users:extra_groups').split()
    admin_groups = it.get('users:admin_groups').split()
    sysadmin_groups = it.get('users:sysadmin_groups').split()
    grouplist = extra_groups + admin_groups + sysadmin_groups
    groups = list(set(grouplist))
    return groups

def get_target_groups(toolkit):
    it = toolkit
    cmd  = ['getent', 'group']
    proc = it.chroot_proc(cmd, stdout=it.PIPE)
    retval = proc.wait()
    if retval:
        raise it.CmdLineError, "Command %s returned %d" % (' '.join(cmd), retval)
    lines = [line.strip() for line in proc.stdout]
    groups = [line.split(':')[0] for line in lines]
    return groups

def get_undefined_groups(toolkit):
    defined = get_all_defined_groups(toolkit)
    created = get_target_groups(toolkit)
    to_be_created = [g for g in defined if g not in created]
    return to_be_created

    
def make_groups(toolkit):
    it = toolkit
    current_trait = it.trait
    it.set_trait('users')
    new_groups = get_undefined_groups(it)
    print "Creating groups: %s" % ', '.join(new_groups)
    # pretend these are all user groups
    addgroup = ['addgroup']
    for group in new_groups:
        print "creating group %s" % group
        cmd = addgroup + [group]
        it.chroot(cmd)
    # down here at the end
    it.set_trait(current_trait)
    
def set_plaintext_password(toolkit, username, password):
    it = toolkit
    yes_proc = it.proc(['yes', password], stdout=it.PIPE)
    pass_proc = it.chroot_proc(['passwd', username], stdin=yes_proc.stdout)
    pass_proc.wait()
    print "Set (plaintext) password for", username
    sys.stdout.flush()
    
def get_all_users(toolkit):
    it = toolkit
    current_trait = it.trait
    it.set_trait('users')
    env = it.env()
    standard_users = it.get('users:standard_users').split()
    admin_users = it.get('users:admin_users').split()
    sysadmin_users = it.get('users:sysadmin_users').split()
    # a quick hack to get unique users
    users = list(set(standard_users + admin_users + sysadmin_users))
    username_data = dict(standard=standard_users, admin=admin_users,
                         sysadmin=sysadmin_users, all=users)
    it.set_trait(current_trait)
    return username_data

def get_home_dir(toolkit, user, target=True):
    it = toolkit
    dhome = it.get('users:dhome')
    while dhome.startswith('/'):
        dhome = dhome[1:]
    if target:
        homedir = it.target / dhome / user
    else:
        homedir = path('/') / dhome / user
    return homedir

def make_users(toolkit, username_data=None):
    it = toolkit
    current_trait = it.trait
    it.set_trait('users')
    env = it.env()

    if username_data is None:
        username_data = get_all_users(it)
    standard_users = username_data['standard']
    admin_users = username_data['admin']
    sysadmin_users = username_data['sysadmin']
    users = username_data['all']
    
    standard_groups = []
    #it.get('users:standard_groups').split()
    admin_groups = it.get('users:admin_groups').split()
    sysadmin_groups = it.get('users:sysadmin_groups').split()
    

    # admin groups include standard groups
    admin_groups = list(set(standard_groups + admin_groups))
    # sysadmin groups include both standard and admin groups
    sysadmin_groups = list(set(admin_groups + sysadmin_groups))
    
    for user in users:
        print "user", user
        groups = standard_groups
        if user in admin_users:
            print "user", user, "is an admin user"
            groups = admin_groups
        if user in sysadmin_users:
            groups = sysadmin_groups

        opts = ['--disabled-password']
        uidkey = 'users:user_%s_uid' % user
        if env.has_key(uidkey):
            opts += ['--uid', env.get(uidkey)]
        gecoskey = 'users:user_%s_gecos' % user
        if env.has_key(gecoskey):
            opts += ['--gecos', env.get(gecoskey)]
        else:
            print "pretending that user", user, "has gecos entry"
            opts += ['--gecos', '%s,,,' % user]
        cmd = ['adduser'] + opts + [user]
        print "adding user with command %s" % ' '.join(cmd)
        sys.stdout.flush()
        it.chroot(cmd)
        cmd = ['passwd', '-d', user]
        print "making empty password for", user
        sys.stdout.flush()
        it.chroot(cmd)
        for group in groups:
            cmd = ['adduser', user, group]
            print "Running: %s" % ' '.join(cmd)
            sys.stdout.flush()
            it.chroot(cmd)
        # make ssh directory if sshkeys is present
        envkey = 'users:user_%s_sshkeys' % user
        if env.has_key(envkey):
            print "%s has sshkeys option" % user
            homedir = get_home_dir(it, user)
            if not homedir.isdir():
                raise RuntimeError , "Home directory %s should exist." % homedir
            sys.stdout.flush()
            sshdir = homedir / '.ssh'
            if not sshdir.isdir():
                print "creating ~/.ssh for", user
                sshdir.mkdir()
            sshdir.chmod(0750)
            authkey_filename = sshdir / 'authorized_keys'
            if not authkey_filename.isfile():
                print "creating ~/.ssh/authorized_keys for", user
                sshkeys = env[envkey]
                authkey_filename.write_text(sshkeys)
            authkey_filename.chmod(0640)
            #cmd = ['chown', '-R', '%s:%s' % (user, user), str(sshdir)]
            homedir = get_home_dir(it, user, target=False)
            relsshdir = homedir / '.ssh'
            user_group = '%s:%s' % (user, user)
            cmd = ['chown', '-R', user_group, relsshdir]
            it.chroot(cmd)
        plaintext_key = 'users:user_%s_plaintext_password' % user
        if env.has_key(plaintext_key):
            print "Password to be set for", user
            #password = env[plaintext_key]
            password = it.get(plaintext_key)
            sys.stdout.flush()
            set_plaintext_password(it, user, password)
            
    # down here at the end
    it.set_trait(current_trait)
        
    
def create_dhome(toolkit, dhome):
    cmd = ['mkdir', '-p', dhome]
    toolkit.chroot(cmd)


def update_directory(src, dest, uid, gid):
    for child in src.walk():
        part = child.split(src)[1]
        while part.startswith('/'):
            part = part[1:]
        newname = dest / part
        if child.islink():
            if not newname.islink():
                print "new symlink", part
                target = child.readlink()
                os.symlink(target, newname)
        elif child.isdir():
            if not newname.isdir():
                print "new directory", part
                newname.mkdir()
        elif child.isfile():
            copy = False
            if not newname.isfile():
                copy = True
            else:
                skeltime = child.getmtime()
                hometime = newname.getmtime()
                if hometime < skeltime:
                    copy = True
            if copy:
                print "copying %s" % part
                child.copy(newname)
        else:
            raise RuntimeError , "I don't know what to do with %s" % child
        child.copymode(newname)
        newname.chown(uid, gid)
        
        
    


def update_userhome_from_skel(toolkit, user, skeldir=None):
    it = toolkit
    homedir = get_home_dir(toolkit, user)
    if not homedir.isdir():
        raise RuntimeError , "%s is not a directory" % homedir
    if skeldir is None:
        skeldir = it.target / 'etc/skel'
        if not skeldir.isdir():
            raise RuntimeError , "%s is not a directory" % skeldir
    # we're going to use ~/.bashrc to get the uid and gid
    # of the files that we'll update.
    bashrc = homedir / '.bashrc'
    stat = bashrc.stat()
    uid = stat.st_uid
    gid = stat.st_gid
    update_directory(skeldir, homedir, uid, gid)
    
    

def update_homes_from_skel(toolkit, username_data=None):
    it = toolkit
    if username_data is None:
        username_data = get_all_users(it)
    #print "username_data is", username_data
    #print "type(username_data) is", type(username_data)
    users = username_data['all']
    for user in users:
        print "updating files from /etc/skel for", user
        update_userhome_from_skel(toolkit, user)
        
