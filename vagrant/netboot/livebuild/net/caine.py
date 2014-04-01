import os
import subprocess
import tempfile


from unipath import Path as path
from livebuild import md5sum

from mbr_parser import MBRParser

# You must be root to run this
# Packages required:  live-helper, paella-installer, wget

CAINE_FILENAME = '/opt/common/disk_images/nbcaine2.5.1.dd'
CAINE_MDSUM = 'd94bf0890be2c6e1c9d7301c222aa876'

DOWNLOAD_DIR = path('downloads')


def rmdir(dirname):
    return subprocess.call(['rm', '-fr', dirname])

def local_basename(url):
    # sourceforge url is http://server/path/to/filename/download
    # so we use this trick to get the actual filename
    dirname = os.path.dirname(url)
    basename = os.path.basename(dirname)
    return basename

def download_caine(dldir=DOWNLOAD_DIR):
    if not dldir.isdir():
        print "creating downloads directory..."
        dldir.mkdir()
    basename = path(CAINE_FILENAME).basename()
    dest = dldir / basename
    if not dest.exists():
        cmd = ['cp', '-a', CAINE_FILENAME, str(dest)]
        subprocess.check_call(cmd)
    mysum = md5sum(file(dest))
    if mysum == CAINE_MDSUM:
        print "Success, md5sum of caine image matches. :)"
    else:
        msg = "Improper file:  Please remove %s and try again." % filename
        raise RuntimeError , msg


def mount_caine(filename):
    blocksize = 512
    mount_point = path(tempfile.mkdtemp('_loopback', 'caine_'))
    mbr = MBRParser(file(filename).read(blocksize))
    startLBA = mbr.PartitionTable.Entry0.StartLBA
    
    offset = blocksize * startLBA
    
    cmd = ['mount', '-o', 'loop,offset=%d' % offset]
    cmd += [str(filename), str(mount_point)]
    subprocess.check_call(cmd)
    return mount_point

def copy_caine(mount_point, verbose=False):
    donedir = path('done')
    nfsrootdir = donedir / 'nfsroot/caine/'
    tftpbootdir = donedir / 'tftpboot/caine/'
    cmd = ['rsync', '-a']
    if verbose:
        cmd.append('-v')
    if not mount_point.endswith('/'):
        mount_point = path('%s/' % mount_point)
    cmd += [str(mount_point), str(nfsrootdir)]
    subprocess.check_call(cmd)
    if not tftpbootdir.isdir():
        tftpbootdir.makedirs()
    casper = nfsrootdir / 'casper'
    for basename in ['vmlinuz', 'initrd.gz']:
        src = casper / basename
        dest = tftpbootdir / basename
        cmd = ['cp', src, dest]
        subprocess.check_call(cmd)
        
    
    
if __name__ == "__main__":
    #z = ZipFile(DOWNLOAD_DIR / local_basename(CLONEZILLA_URL))
    #unzip_clonezilla(CLONEZILLA_URL)
    #move_clonezilla_files()
    pass

    
