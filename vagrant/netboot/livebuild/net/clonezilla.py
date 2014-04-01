import os
import subprocess
from zipfile import ZipFile

from useless.base.path import path
from useless.base.util import md5sum

# You must be root to run this
# Packages required:  live-helper, paella-installer, wget
#http://sourceforge.net/projects/clonezilla/files/
CLONEZILLA_URL = "http://sourceforge.net/projects/clonezilla/files/"
CLONEZILLA_URL += "clonezilla_live_stable/OldFiles/1.2.6-40/clonezilla-live-1.2.6-40-i686.zip/download"
#CLONEZILLA_URL += "clonezilla_live_stable/1.2.6-40/clonezilla-live-1.2.6-40-i686.zip/download"
CLONEZILLA_MDSUM = 'cbb3e78fc2bb7dbee2f2e5260413bceb'

DOWNLOAD_DIR = path('downloads')


def rmdir(dirname):
    return subprocess.call(['rm', '-fr', dirname])

def local_basename(url):
    # sourceforge url is http://server/path/to/filename/download
    # so we use this trick to get the actual filename
    dirname = os.path.dirname(url)
    basename = os.path.basename(dirname)
    return basename

def download_clonezilla(url, dldir=DOWNLOAD_DIR):
    if not dldir.isdir():
        print "creating downloads directory..."
        dldir.mkdir()
    basename = local_basename(url)
    filename = dldir / basename
    if filename.isfile():
        print "Clonezilla already downloaded: %s" % basename
    else:
        cmd = ['wget', url, '-O', filename]
        subprocess.call(cmd)
    mysum = md5sum(file(filename))
    if mysum == CLONEZILLA_MDSUM:
        print "Success, md5sum of clonezilla matches. :)"
    else:
        raise RuntimeError , "Improper file:  Please remove %s and try again." % filename
    

def unzip_clonezilla(url, dldir=DOWNLOAD_DIR, destdir='tmp'):
    destdir = path(destdir)
    if not destdir.isdir():
        destdir.mkdir()
    basename = local_basename(url)
    filename = dldir / basename
    zipped = ZipFile(filename)
    for entry in zipped.namelist():
        #print "handling entry,", entry
        entry = path(entry)
        dest = destdir / entry
        if entry.endswith('/') :
            if not dest.isdir():
                dest.makedirs()
        else:
            contents = zipped.read(str(entry))
            dest.write_bytes(contents)

def move_clonezilla_files(srcdir='tmp'):
    srcdir = path(srcdir)
    donedir = path('done')
    livedir = srcdir / 'live'
    # stuff for tftpboot
    vmlinuz = 'vmlinuz1'
    initrd = 'initrd1.img'
    # stuff for nfsroot
    fs = 'filesystem.squashfs'
    fsp = 'filesystem.packages'
    freedos = 'freedos.img'
    # start with nfsroot
    nfsrootdir = donedir / 'nfsroot'
    cz_nfsrootdir = nfsrootdir / 'clonezilla' / 'live'
    if not cz_nfsrootdir.isdir():
        cz_nfsrootdir.makedirs()
    for basename in [fs, fsp, freedos]:
        srcname = livedir / basename
        destname = cz_nfsrootdir / basename
        os.rename(srcname, destname)
    # now to tftpboot
    tftpbootdir = donedir / 'tftpboot'
    cz_tftpbootdir = tftpbootdir / 'clonezilla'
    if not cz_tftpbootdir.isdir():
        cz_tftpbootdir.mkdir()
    for basename in [vmlinuz, initrd]:
        srcname = livedir / basename
        destname = cz_tftpbootdir / basename
        os.rename(srcname, destname)

    
if __name__ == "__main__":
    z = ZipFile(DOWNLOAD_DIR / local_basename(CLONEZILLA_URL))
    unzip_clonezilla(CLONEZILLA_URL)
    move_clonezilla_files()
    
    
