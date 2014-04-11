import os
import tempfile
import subprocess

def make_deplist(listed, all, setfun, parfun, log=None):
    deplist = []
    while len(listed):
        deplist_prepended = False
        dep = listed[0]
        setfun(dep)
        parents = parfun()
        #print parents
        if len(parents) and type(parents[0]) != str:
            #print parents, type(parents[0])
            parents = [r[0] for r in parents]
        for p in parents:
            if not deplist_prepended and p not in deplist:
                listed = [p] + listed
                deplist_prepended = True
                if log:
                    log.info('deplist prepended with %s' % p)
        if not deplist_prepended:
            deplist.append(dep)
            del listed[0]
        if log:
            log.info('%s %s' % (str(deplist), str(listed)))
    cleanlist = []
    for dep in deplist:
        if dep not in cleanlist:
            cleanlist.append(dep)
    return cleanlist

def edit_dbfile(name, data, ftype='script'):
    tmp, path = tempfile.mkstemp('paella', ftype)
    tmp = file(path, 'w')
    tmp.write(data)
    tmp.close()
    os.system('$EDITOR %s' %path)
    tmp = file(path, 'r')
    mod = tmp.read()
    tmp.seek(0)
    tmp.close()
    os.remove(path)
    if mod != data:
        return mod
    else:
        return None
        

def get_architecture():
    proc = subprocess.Popen(['dpkg', '--print-architecture'],
                            stdout=subprocess.PIPE)
    arch = proc.stdout.read().strip()
    retcode = proc.wait()
    if retcode:
        raise RuntimeError , "dpkg returned %d" % retcode
    if os.environ.has_key('PAELLA_ARCH_OVERRIDE'):
        arch = os.environ['PAELLA_ARCH_OVERRIDE']
    return arch

    
