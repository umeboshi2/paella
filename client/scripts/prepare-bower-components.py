import os, sys
import subprocess
import json

COMPONENT_PATH = 'bower_components'
#DEST_PATH = os.path.join('client','components')
DEST_PATH = 'components'


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
    'bower_components/outlayer/item.js',
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
    if type(pathspec) is not list:
        raise RuntimeError, "pathspec for fontawesome must be a list."
    name = 'font-awesome'
    for path in pathspec:
        if path.endswith('*'):
            path = os.path.dirname(path)
            files = os.listdir(path)
            for filename in files:
                fpath = os.path.join(path, filename)
                handle_file(fpath)
        elif os.path.isdir(path):
            handle_dir(name, path)
        elif os.path.isfile(path):
            handle_file(path)
        else:
            raise RuntimeError, "Don't know what to do with %s." % path
        
def handle_ace_editororig(components):
    basedir = os.path.join(components, 'ace-builds/src')
    print "Handling ace"
    for basename in os.listdir(basedir):
        pathspec = os.path.join(basedir, basename)
        handle_file(pathspec)
        

def handle_ace_editor(components):
    libdir = os.path.join(COMPONENT_PATH, 'ace/lib')
    print "LIBDIR", libdir
    components_dir = os.path.join(components, 'ace')
    print "DEPLOY", components_dir
    if not os.path.isdir(components_dir):
        os.makedirs(components_dir)
    cmd = ['cp', '-a', libdir, components_dir]
    subprocess.check_call(cmd)
    
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
    dest = os.path.join(DEST_PATH, dpath)
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
    if name == 'font-awesome':
        handle_fontawesome(pathspec)
        return
    if name not in IGNORED:
        handle_generic_component(name, pathspec)
        
    





if __name__ == '__main__':
    paths = get_paths()
    for name, pathspec in paths.items():
        handle_item(name, pathspec)
    for path in SPECIAL_PATHS:
        handle_file(path)
    ace_path = os.path.join(COMPONENT_PATH, 'ace')
    if os.path.isdir(ace_path):
        handle_ace_editor(DEST_PATH)
        
