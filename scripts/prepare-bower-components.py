import os, sys
import subprocess
import json


# I will only need one of these two
IGNORED_NEEDED = ['ace', 'ace-builds']

# backbone.modal needs special handling
IGNORED_NEEDED += ['backbone.modal']

# font-awesome is already handled with compass
# the other components are for testing
IGNORED_TESTING = ['fine-uploader',
                   'leaflet', 'videojs', 'tag-it',
                   'jqueryui-timepicker-addon']

# I have been using my other copy of requirejs
# I probably don't need the r.js client side
IGNORED_NOT_NEEDED = ['r.js',]


IGNORED = IGNORED_NEEDED + IGNORED_TESTING + IGNORED_NOT_NEEDED


SPECIAL_PATHS = [
    'bower_components/bootstrap/js/modal.js',
    ]


# TODO
# create special preps for ace


def get_paths():
    cmd = ['bower', 'list', '--json', '--paths']
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    retcode = proc.wait()
    if retcode:
        raise RuntimeError, "Returned %d" % retcode
    paths = proc.stdout.read()
    return json.loads(paths)

def npm_package_filename(pathspec):
    return os.path.join(pathspec, 'package.json')

def is_npm_package(pathspec):
    filename = npm_package_filename(pathspec)
    return os.path.isfile(filename)

def parse_npm_package(pathspec):
    filename = npm_package_filename(pathspec)
    return json.load(file(filename))


def handle_fontawesome(pathspec):
    srcdir = os.path.join(pathspec, 'fonts')
    fonts = os.listdir(srcdir)
    for basename in fonts:
        src = os.path.join(srcdir, basename)
        handle_file(src)
        
def handle_requirejs(pathspec):
    filename = os.path.join(pathspec, 'require.js')
    if not os.path.isfile(filename):
        msg = "RequireJS not found %s" % filename
        raise RuntimeError, msg
    handle_file(filename)
    
def handle_file(pathspec):
    src = pathspec
    #dest = os.path.join('trumpet', 'static', src)
    dpath = pathspec
    bower_dir = 'bower_components/'
    if dpath.startswith(bower_dir):
        dpath = dpath[len(bower_dir):]
    dest = os.path.join('components', dpath)
    dirname = os.path.dirname(dest)
    if not os.path.isdir(dirname):
        os.makedirs(dirname)
    if not os.path.isfile(dest):
        print "Copying to ", dest
        cmd = ['cp', '-a', src, dest]
        subprocess.check_call(cmd)

def handle_nodejs_package(name, pathspec):
    pkg = parse_npm_package(pathspec)
    if 'main' not in pkg:
        print "Can't handle", name
    else:
        main = pkg['main']
        if not main.endswith('.js'):
            main = '%s.js' % main
        filename = os.path.join(pathspec, main)
        if not os.path.isfile(filename):
                msg = "%s not found for %s" % (pathspec, name)
                raise RuntimeError, msg
        handle_file(filename)
        
def handle_dir(name, pathspec):
    if is_npm_package(pathspec):
        if name == 'font-awesome':
            handle_fontawesome(pathspec)
        else:
            handle_nodejs_package(name, pathspec)
    else:
        # test for name.js
        basename = '%s.js' % name
        filename = os.path.join(pathspec, basename)
        if not os.path.isfile(filename):
            if name == 'requirejs-bower':
                handle_requirejs(pathspec)
            elif name not in IGNORED:
                raise RuntimeError, "Unable to deal with %s" % name
            else:
                print "IGNORING", name
        else:
            handle_file(filename)
            
def handle_single_item(name, pathspec):
    if os.path.isfile(pathspec):
        handle_file(pathspec)
    elif os.path.isdir(pathspec):
        handle_dir(name, pathspec)
    else:
        print "PATHSPEC", pathspec
        raise RuntimeError, "INVALID PATH FOR %s" % name
    
        

def handle_list_item(name, pathspecs):
    has_dir_path = False
    for p in pathspecs:
        if os.path.isdir(p):
            has_dir_path = True
    if has_dir_path:
        print "%s has a list of pathspecs" % name
    else:
        for p in pathspecs:
            handle_single_item(name, p)

def handle_generic_component(name, pathspec):
    if type(pathspec) is list:
        handle_list_item(name, pathspec)
    else:
        handle_single_item(name, pathspec)    
            
def handle_item(name, pathspec):
    if name not in IGNORED:
        handle_generic_component(name, pathspec)
        
    





if __name__ == '__main__':
    paths = get_paths()
    for name, pathspec in paths.items():
        handle_item(name, pathspec)
    for path in SPECIAL_PATHS:
        handle_file(path)
