import subprocess

from livebuild.path import path

def rmdir(dirname):
    return subprocess.call(['rm', '-fr', dirname])

def remove_chroot():
    dirname = path('chroot')
    if dirname.isdir():
        print "chroot/ exists......removing"
        rmdir(str(dirname))
    if dirname.exists():
        raise RuntimeError , "chroot/ not removed correctly."
    
def setup_cachedirs(archs):
    dirnames = ['chroot.%s' % a for a in archs]
    extract = True
    dirfound = False
    for dirname in dirnames:
        if path(dirname).isdir():
            dirfound = True
            extract = False
        else:
            extract = True
    if extract and dirfound:
        print "WARNING, something funny is happening..."
    filename = path('cachedirs.tar.gz')
    if filename.exists() and extract:
        print "extracting cache directories..."
        cmd = ['tar', 'xfz', str(filename)]
        retval =  subprocess.call(cmd)
        if retval:
            print "RETVAL: %d" % retval
            raise RuntimeError , "Something bad happened when extracting %s" % filename

def create_cachedirs_tarball():
    filename = path('cachedirs.tar.gz')
    if not filename.exists():
        print "Creating %s" % filename
        cmd = ['tar', 'cfz', str(filename), 'chroot.amd64', 'chroot.i386']
        retval = subprocess.call(cmd)
        if retval:
            print "RETVAL: %d" % retval
            raise RuntimeError , "Something bad happened with creating %s ." % filename
    else:
        print "%s already exists, skipping this step." % filename
        
    
    

if __name__ == "__main__":
    pass
