
import os, os.path, sys
from os.path import join
from shutil import copytree


os.system('mount /cdrom')

root = '/mirrors/share/mp3cds'

ls = os.listdir(root)

ls = [x for x in ls if x[:2] == 'cd']

n = len(ls)

newdir = 'cd-%03d'  % (n + 1)

npath = join(root, newdir)
#os.mkdir(npath)
copytree('/cdrom', npath)
print 'copying to ', npath
os.system('umount /cdrom')
print 'Done'
os.system('eject /dev/scd0')
