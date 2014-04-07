import os, sys
from optparse import OptionParser

parser = OptionParser()

parser.add_option('-v', '--verbose', action='store_true', dest='verbose',
                  default=False)
parser.add_option('-i', '--install', action='store_true', dest='install',
                  default=False,
                  help='Mark packages as "install" instead of "hold" or "deinstall"')
parser.add_option('-d', '--dist', action='store', dest='dist',
                  default='wheezy')


opts, args = parser.parse_args(sys.argv[1:])


MASTERLISTS = dict(wheezy='wheezy.pkgs')

def make_pkg_line(package, action):
    # These are magic numbers to more closely mimic
    # the output of dpkg --get-selections
    truetab = 6 - (len(package) / 8)
    tabs = '\t' * truetab
    if not tabs:
        tabs = '\t'
    line = '%s%s%s\n' % (package, tabs, action)
    return line

def file_to_dictionary(filename):
    data = dict()
    for line in file(filename):
        line = line.strip()
        package, action = [i.strip() for i in line.split()]
        #print '%s: %s' % (package, action)
        multiarch_stripped = False
        if ':' in package:
            print "multiarch detected: %s" % package
            package = package.split(':')[0]
            multiarch_stripped = True
        if package in data and not multiarch_stripped:
            msg = 'Package %s already present...' % package
            raise RuntimeError, msg
        else:
            if opts.install:
                action = 'install'
            if action != 'install':
                print "WARNING: %s set for action %s" % (package, action)
            data[package] = action
    return data

def get_master_list(dist):
    filename = MASTERLISTS[dist]
    return file_to_dictionary(filename)

def make_master_file(dist, data):
    master_filename = MASTERLISTS[dist]
    mfile = file(master_filename, 'w')
    packages = data.keys()
    packages.sort()
    for package in packages:
        action = data[package]
        line = make_pkg_line(package, action)
        mfile.write(line)
    mfile.close()
        
    
def update_master_list(dist, filenames):
    master_filename = MASTERLISTS[dist]
    if not os.path.isfile(master_filename):
        print "creating new file: %s" % master_filename
        m = file(master_filename, 'w')
        m.close()
    master_data = get_master_list(opts.dist)
    for filename in filenames:
        print "updating %s with %s" % (master_filename, filename)
        data = file_to_dictionary(filename)
        master_data.update(data)
    print "Updating %s with all gathered data" % master_filename
    make_master_file(dist, master_data)
    

def main(opts, args):
    if not args:
        msg = "please provide a list as an argument"
        raise RuntimeError , msg
    if opts.dist not in MASTERLISTS:
        msg = 'Dist %s not defined.' % opts.dist
        raise RuntimeError, msg
    for filename in args:
        if not os.path.isfile(filename):
            msg = '%s is not a file' % filename
            raise RuntimeError, msg
    update_master_list(opts.dist, args)
    
if __name__ == '__main__':
    main(opts, args)
    
    
