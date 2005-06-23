import os, sys
from kjbuckets import kjGraph, kjSet

from useless.base.util import ujoin
from useless.db.lowlevel import InstallerConnection
from useless.db.midlevel import StatementCursor

from base import TraitParent, TraitPackage
from base import get_traits, get_suite


actions = ['remove', 'purge', 'install']

commands = {'install' : 'apt-get -y --force-yes --fix-missing install',
	    'remove'  : 'apt-get -y remove',
	    'purge'  : 'apt-get -y --purge remove',
            'dselect-upgrade' : 'apt-get -y dselect-upgrade',
            'taskinst' : 'tasksel -n install',
            'hold' : 'dpkg --set-selections',
            'clean' : 'apt-get clean'
            }
def spaced(*args):
    return ' '.join(args)

def make_command(command, parsed, root=None):
    packages = spaced(*parsed[command])
    aptcommand = spaced(commands[command], packages)
    if root:
        aptcommand = 'chroot %s %s' % (root, aptcommand)
    return aptcommand

def make_all_commands(packages, root=None):
    parsed = parse_package_rows(packages)
    all_commands = []
    for command in actions:
        all_commands.append(make_command(command, parsed, root=root))
    return all_commands

def make_sources_list(sources, target='/'):
    aptdir = join(target, 'etc', 'apt')
    makepaths(aptdir)
    sources_list = file(join(aptdir, 'sources.list'), 'w')
    for source in sources:
        sources_list.write(str(source) + '\n')
    sources_list.close()
    

if __name__ == '__main__':
    c = InstallerConnection()
    tp = TraitParent(c, 'woody')
    pp = TraitPackage(c, 'woody')
    packs = pp.all_packages(['DEFAULT'], tp)
    parsed = parse_package_rows(packs)
    rac = run_all_commands
