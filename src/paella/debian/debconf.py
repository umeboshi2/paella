import os
import rfc822


from apt_pkg import ParseTagFile


from useless.base import debug, Error
from useless.base.util import strfile


def _parse_tagfile(filename, function):
    pdict = {}
    tagfile = file(filename)
    parser = ParseTagFile(tagfile)
    while parser.Step():
        k,v = function(parser.Section)
        pdict[k] = v
    return pdict

def parse_configdb(path):
    cf = file(path).read()
    return map(rfc822.Message, [strfile(x + '\n') for x in cf.split('\n\n')[:-1]])

def make_src_item(section):
    pkg = section['package']
    dir = section['directory']
    files = split_filelist(section['files'])
    return pkg, (dir, files)

def make_section(section):
    pkg = section['package']
    sdict = {}
    for k in section.keys():
        sdict[k.lower()] = section[k]
    return pkg, sdict

def make_debconf_section(section):
    conf = section['name']
    sdict = {}
    for k in section.keys():
        sdict[k.lower()] = section[k]
    return conf, sdict

def make_template_section(section):
    conf = section['template']
    sdict = {}
    for k in section.keys():
        sdict[k.lower()] = section[k]
    return conf, sdict
    

def parse_debconf(filename):
    return _parse_tagfile(filename, make_debconf_section)

def parse_debconf_template(filename):
    return _parse_tagfile(filename, make_template_section)

def _copt(name, value):
    return '-c %s:%s' %(name, value)

def backup_debconf_section(package, filename, run=True):
    dbname = _copt('Name', 'backup')
    driver = _copt('Driver', 'File')
    dbfile = _copt('FileName', filename)
    cmd = 'debconf-copydb configdb backup --owner-pattern=' % package
    opts = ' '.join([dbname, driver, dbfile])
    cmd = ' '.join([cmd, opts])
    if run:
        os.system(cmd)
    else:
        return cmd

def restore_debconf_section(package, filename, run=True):
    dbname = _copt('Name', 'backup')
    driver = _copt('Driver', 'File')
    dbfile = _copt('FileName', filename)
    cmd = 'debconf-copydb backup configdb --owner-pattern=' % package
    opts = ' '.join([dbname, driver, dbfile])
    cmd = ' '.join([cmd, opts])
    if run:
        os.system(cmd)
    else:
        return cmd

def install_debconf(config=None, target=None, run=False):
    config_dbname = _copt('Name', 'installer')
    target_dbname = _copt('Name', 'target')
    driver = _copt('Driver', 'File')
    config_dbfile = _copt('FileName', config)
    target_dbfile = _copt('FileName', target)
    cmd = 'debconf-copydb installer target'
    config_options = ' '.join([config_dbname, driver, config_dbfile])
    target_options = ' '.join([target_dbname, driver, target_dbfile])
    command = ' '.join([cmd, config_options, target_options])
    if run:
        os.system(command)
    else:
        return command

def copy_configdb(src_path, dest_path):
    srcdb = parse_configdb(src_path)
    destdb = parse_configdb(dest_path)
    _max_inserts = len(srcdb) + len(destdb)
    newdb = []
    while len(srcdb) or len(destdb):
        if not len(destdb):
            destdb.append(srcdb[0])
        record = destdb.pop(0)
        name = record['name']
        snames = [x['name'] for x in srcdb]
        if name in snames:
            ind = snames.index(name)
            record = srcdb[ind]
            srcdb.pop(ind)
        newdb.append(record)
        while len(srcdb) and srcdb[0]['name'] < name:
            newdb.append(srcdb.pop(0))
            if len(newdb) > _max_inserts:
                raise Error, 'bad looping in copy_configdb'
        if len(newdb) > _max_inserts:
            raise Error, 'bad looping in copy_configdb'
    data = '\n'.join(map(str, newdb))
    target = file(dest_path, 'w')
    target.write(data)
    target.close()
    
if __name__ == '__main__':
    fname = '/var/cache/debconf/config.dat'
    p = parse_debconf(fname)
    
