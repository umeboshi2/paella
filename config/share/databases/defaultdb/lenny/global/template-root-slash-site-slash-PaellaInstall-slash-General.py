# -*- mode: python -*-
import os, sys
import base64

from useless.base.path import path

from paella.installer.util.base import install_packages_command

class BaseExistsError(Exception):
    pass

class NoExistError(BaseExistsError):
    pass

class AlreadyExistsError(BaseExistsError):
    pass

DEFAULT_BACKUP_DIR = 'etc/paella-interfering-files'

def remove_leading_slash(pathname):
    while pathname.startswith('/'):
        pathname = pathname[1:]
    return pathname

def install_packages(toolkit, packages, trait=None, usertag=None):
    it = toolkit
    if trait is None:
        trait = it.trait
    if usertag is None:
        usertag = 'paella-trait-%s' % trait
    #cmd = ['aptitude', '--assume-yes', '--add-user-tag', usertag,
    #       'install'] + packages
    cmd = install_packages_command(packages, it.default, trait=trait, usertag=usertag)
    print "Install command is %s" % ' '.join(cmd)
    sys.stdout.flush()
    it.chroot(cmd)
    
def run_machine_script(toolkit, name, machine):
    it = toolkit
    scriptdb = it.db.machine.relation.scripts
    scriptfile = scriptdb.get(name, machine=machine)
    script_basename = 'tmp/%s-%s' % (machine, name)
    scriptname = it.target / script_basename
    if scriptname.exists():
        raise RuntimeError , "%s already exists." % scriptname
    newfile = scriptname.open('w')
    block = scriptfile.read(1024)
    while block:
        newfile.write(block)
        block = scriptfile.read(1024)
    newfile.close()
    scriptname.chmod(0755)
    cmd = [scriptname]
    it.run(cmd)
    scriptname.remove()
    if scriptname.exists():
        raise RuntimeError , "%s was not deleted." % scriptname
    
        
    
def relocate_interfering_files(toolkit, filenames, backup_dir=None):
    it = toolkit
    if backup_dir is None:
        backup_dir = DEFAULT_BACKUP_DIR
    backup_dir = remove_leading_slash(backup_dir)
    full_backup_dir = it.target / backup_dir
    if not full_backup_dir.isdir():
        print "creating %s" % full_backup_dir
        sys.stdout.flush()
        full_backup_dir.makedirs()
    for filename in filenames:
        print "relocating %s" % filename
        filename = remove_leading_slash(filename)
        current_filename = it.target / filename
        backup_filename = full_backup_dir / filename
        if backup_filename.exists():
            raise AlreadyExistsError , "%s already exists." % backup_filename
        if not current_filename.exists():
            raise NoExistError , "%s doesn't exist." % current_filename
        if current_filename.islink():
            # we aren't handling links right now
            raise RuntimeError , "%s is a link." % current_filename
        if current_filename.isfile():
            # we are relocating a file instead of a directory
            dirname = backup_filename.dirname()
            if not dirname.isdir():
                dirname.makedirs()
            print "relocating %s to %s" % (current_filename, backup_filename)
            os.rename(current_filename, backup_filename)
            sys.stdout.flush()
        else:
            raise RuntimeError , "Unable to handle %s" % current_filename
        
            
            

def restore_intefering_files(toolkit, backup_dir=None):
    it = toolkit
    if backup_dir is None:
        backup_dir = DEFAULT_BACKUP_DIR
    backup_dir = remove_leading_slash(backup_dir)
    full_backup_dir = it.target / backup_dir
    if not full_backup_dir.isdir():
        print "There is no backup directory, skipping restore."
        return
    for filename in full_backup_dir.walkfiles():
        shortname = filename.split(full_backup_dir)[1]
        shortname = remove_leading_slash(shortname)
        newname = it.target / shortname
        if newname.isfile():
            raise AlreadyExistsError , "%s already exists." % newname
        # we hope that the directory that the filename was in wasn't
        # removed after we moved the file that we are restoring.
        print "Restoring %s" % newname
        sys.stdout.flush()
        os.rename(filename, newname)
    # here we will cleanup the backup directory
    for root, dirs, files in os.walk(full_backup_dir, topdown=False):
        #print root, dirs, files
        if dirs:
            # if there are dirs, we'll test for existence then rmdir
            for adir in dirs:
                fullpath = os.path.join(root, adir)
                if os.path.isdir(fullpath):
                    os.rmdir(fullpath)
                else:
                    print "%s isn't really there, skipping." % fullpath
        if files:
            print "Error, leftover files %s" % files
            print "root, %s" % root
        os.rmdir(root)
    if full_backup_dir.isdir():
        raise RuntimeError , "Something happened, as %s wasn't removed." % full_backup_dir


    
def decode_base64_templates(toolkit, trait=None, suffix='.b64',
                            removefiles=True, verbose=False):
    it = toolkit
    current_trait = it.trait
    if trait is not None:
        if verbose:
            print "Setting trait to %s" % trait
        it.set_trait(trait)
    templates = it.db.trait.templates()
    b64_templates = [t for t in templates if t.endswith(suffix)]
    if verbose:
        print "base64 templates: %s" % b64_templates
    for template in b64_templates:
        if verbose:
            print "decoding %s" % template
        filename = it.target / template
        encoded_data = filename.bytes()
        decoded_data = base64.b64decode(encoded_data)
        truncate_position = - len(suffix)
        new_filename = path(filename[:truncate_position])
        new_filename.write_bytes(decoded_data)
        if verbose:
            print "Created %s" % new_filename
        if removefiles:
            if verbose:
                print "Removing %s" % filename
            filename.remove()
    # set the trait back
    it.set_trait(current_trait)
        
