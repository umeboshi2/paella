import os
from os.path import isdir, isfile, join, basename, dirname
from sets import Set
from ConfigParser import RawConfigParser
import tempfile

from kjbuckets import kjGraph, kjSet

from useless.base import Error, NoExistError
from useless.base.util import ujoin, makepaths, md5sum, strfile
from useless.base.objects import Parser

from useless.sqlgen.clause import one_many, Eq, In, NotIn

from useless.base.config import Configuration, list_rcfiles
from useless.base.template import Template as _Template

from useless.db.lowlevel import QuickConn
from useless.db.midlevel import StatementCursor
from useless.db.midlevel import Environment, TableDict
from useless.db.midlevel import SimpleRelation

class PaellaConfig(Configuration):
    def __init__(self, section=None, files=list_rcfiles('paellarc')):
        if section is None:
            section = 'database'
        Configuration.__init__(self, section=section, files=files)
        

class PaellaConnection(QuickConn):
    def __init__(self, cfg=None):
        if cfg is None:
            cfg = PaellaConfig('database')
        if type(cfg) is not dict:
            dsn = cfg.get_dsn()
        else:
            dsn = cfg
        if os.environ.has_key('PAELLA_DBHOST'):
            dsn['dbhost'] = os.environ['PAELLA_DBHOST']
        if os.environ.has_key('PAELLA_DBNAME'):
            dsn['dbname'] = os.environ['PAELLA_DBNAME']
        QuickConn.__init__(self, dsn)

class ProfileStruct(object):
    name = 'myprofile'
    suite = 'sid'
    traits = ['admin']
    environ = {}
    template = 'path_to_template'

class TraitStruct(object):
    name = 'mytrait'
    suite = 'sid'
    parents = ['another_trait', 'maybe_another_trait']
    packages = dict.fromkeys(['bash', 'apache', 'python'], 'install')
    environ = {'name' : 'value'}
    templates = ['rel_path_to_template1',
                 'rel_path_to_template2']


class Suites(StatementCursor):
    def __init__(self, conn):
        StatementCursor.__init__(self, conn, name='Suites')
        self.set_table('suites')
        self.current = None

    def list(self):
        return [x.suite for x in self.select()]

    def set(self, suite):
        if suite not in self.list():
            raise Error, 'bad suite'
        self.current = suite

class AllTraits(StatementCursor):
    def __init__(self, conn):
        StatementCursor.__init__(self, conn, name='AllTraits')
        self.set_table('traits')

    def list(self):
        return [x.trait for x in self.select()]

class Traits(StatementCursor):
    def __init__(self, conn, suite):
        StatementCursor.__init__(self, conn, name='AllTraits')
        self.set_suite(suite)
        
        
    def set_suite(self, suite):
        self.suite = suite
        self.set_table(ujoin(self.suite, 'traits'))
        

    def list(self):
        return [x.trait for x in self.select(order=['trait'])]
    

class TraitEnvironment(Environment):
    def __init__(self, conn, suite, trait):
        self.suite = suite
        table = ujoin(suite, 'variables')
        Environment.__init__(self, conn, table, 'trait')
        self.set_main(trait)

class TraitEnvironments(Environment):
    def __init__(self, conn, suite):
        self.suite = suite
        table = ujoin(suite, 'variables')
        Environment.__init__(self, conn, table, 'trait')

    def set_trait(self, trait):
        self.set_main(trait)

class _TraitRelation(SimpleRelation):
    def __init__(self, conn, suite, table, name='_TraitRelation'):
        SimpleRelation.__init__(self, conn, table, 'trait', name=name)
        self.suite = suite
        self.current_trait = None

    def set_trait(self, trait):
        self.set_current(trait)
        self.current_trait = self.current
        

    def delete_trait(self, trait):
        self.delete(trait)
        
    
class _CommonTemplate(object):
    def template_filename(self, template):
        tpath = join(self.template_path, self.suite, self.trait)
        return join(tpath, template + '.template')

    def suite_template_path(self, filesel=False):
        path = join(self.template_path, self.suite)
        if filesel:
            path += '/'
        return path

    def trait_temp_path(self, filesel=False):
        path = join(self._tmp_path, self.suite, self.trait)
        if filesel:
            path += '/'
        return path

    def set_suite(self, suite):
        self.suite = suite


class Template(_Template):
    def __init__(self, data={}):
        _Template.__init__(self, data)
        self.template_path = None

    def set_path(self, path):
        self.template_path = path
        
    #this returns the path from the root
    #of the trait tarfile to the template
    def _template_filename(self, suite, trait, package, template):
        tpath = join(self.template_path, suite, trait, package)
        return join(tpath, template + '.template')

    def _filesel(self, filesel, path):
        if filesel:
            path += '/'
        return path

    def _suite_template_path(self, suite, filesel=False):
        return self._filesel(filesel, join(self.template_path, suite))

    def _trait_temp_path(self, tmp_path, suite, trait, filesel=False):
        return self._filesel(filesel, join(tmp_path, suite, trait))
    
    def set_template(self, templatefile):
        _Template.set_template(self, templatefile.read())
        templatefile.close()

    def set_suite(self, suite):
        self.suite = suite

    def set_trait(self, trait):
        self.trait = trait
        

class TextFileManager(object):
    def __init__(self, conn):
        object.__init__(self)
        self.conn = conn
        self.cursor = StatementCursor(self.conn)
        self.cursor.set_table('textfiles')

    def insert_file(self, datafile):
        md5 = self._md5sum(datafile)
        data = datafile.read()
        md5size = '_'.join([md5, str(len(data))])
        return self._insert_data(md5size, data)

    def insert_data(self, data):
        md5 = md5sum(strfile(data))
        md5size = '_'.join([md5, str(len(data))])
        return self._insert_data(md5size, data)
    
    def _insert_data(self, md5size, data):
        clause=Eq('md5size', md5size)
        try:
            row = self.cursor.select_row(clause=clause)
        except NoExistError:
            row = None
        if not row:
            self.cursor.insert(data={'md5size' : md5size, 'data' : data})
            row = self.cursor.select_row(clause=clause)
        return row.fileid

    def get_data(self, id):
        row = self.cursor.select_row(clause=Eq('fileid', id))
        return row.data

    def get_strfile(self, id):
        return strfile(self.get_data(id))

    def _md5sum(self, datafile):
        datafile.seek(0)
        md5 = md5sum(datafile)
        datafile.seek(0)
        return md5
    
def get_traits(conn, profile):
    cursor = StatementCursor(conn)
    cursor.set_table('profile_trait')
    cursor.set_clause([('profile', profile)])
    return [r.trait for r in cursor.select()]

def get_suite(conn, profile):
    cursor = StatementCursor(conn)
    cursor.set_table('profiles')
    cursor.set_clause([('profile', profile)])
    return [r.suite for r in cursor.select()][0]

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

class VariablesConfig(RawConfigParser):
    def __init__(self, conn, table, section,
                 mainfield=None, mainvalue=None,
                 option='name', value='value'):
        self.conn = conn
        self.cursor = StatementCursor(self.conn)
        self.cursor.set_table(table)
        self._secfield = section
        bothnone = mainfield is None and mainvalue is None
        bothset = mainfield and mainvalue
        if not bothnone and not bothset:
            raise Error, 'both mainfield and mainvalue need to be set/unset'
        self._mainclause = None
        if bothset:
            self._mainclause = Eq(mainfield, mainvalue)
        self._fields = [self._secfield, option, value]
        RawConfigParser.__init__(self)
        for row in self.cursor.select(fields=self._fields, clause=self._mainclause):
            if row[0] not in self.sections():
                self.add_section(row[0])
            self.set(*row)

    def write(self, cfile):
        sections = self.sections()
        sections.sort()
        for section in sections:
            cfile.write('[%s]\n' % section)
            keys = self.options(section)
            keys.sort()
            for k in keys:
                if k != '__name__':
                    v = str(self.get(section, k)).replace('\n', '\n\t')
                    cfile.write('%s:\t%s\n' % (k, v))
            cfile.write('\n')
            
    def edit(self):
        tmp, path = tempfile.mkstemp('variables', 'config')
        tmp = file(path, 'w')
        self.write(tmp)
        tmp.close()
        os.system('$EDITOR %s' % path)
        tmp = file(path, 'r')
        newconfig = RawConfigParser()
        newconfig.readfp(tmp)
        tmp.close()
        os.remove(path)
        return newconfig

    def diff(self, other):
        ltmp, lpath = tempfile.mkstemp('variables', 'config')
        ltmp = file(lpath, 'w')
        self.write(ltmp)
        ltmp.close()
        rtmp, rpath = tempfile.mkstemp('variables', 'config')
        rtmp = file(rpath, 'w')
        other.write(rtmp)
        rtmp.close()
        os.system('xxdiff %s %s' % (lpath, rpath))
        ltmp, rtmp = file(lpath, 'r'), file(rpath, 'r')
        lcfg, rcfg = RawConfigParser(), RawConfigParser()
        lcfg.readfp(ltmp)
        rcfg.readfp(rtmp)
        ltmp.close()
        rtmp.close()
        self.update(lcfg)
        other.update(rcfg)
        
    
        
    def update(self, newconfig):
        removed = [x for x in self.sections() if x not in newconfig.sections()]
        for section in removed:
            print 'removing', section
            sclause = Eq(self._secfield, section)
            if self._mainclause:
                sclause &= self._mainclause
            self.cursor.delete(clause=sclause)
        for section in newconfig.sections():
            print section
            sclause = Eq(self._secfield, section)
            if self._mainclause:
                sclause = self._mainclause & Eq(self._secfield, section)
            if not self.has_section(section):
                for k,v in newconfig.items(section):
                    idata = dict(zip(self._fields, [section, k, v]))
                    if self._mainclause:
                        idata[self._mainclause.left] = self._mainclause.right
                    print idata
                    self.cursor.insert(data=idata)
            else:
                for name, value in newconfig.items(section):
                    nclause = sclause & Eq(self._fields[1], name)
                    #print 'nclause', nclause
                    #print 'value', self.get(section, name)
                    if self.has_option(section, name):
                        if value != self.get(section, name):
                            #print 'updating'
                            self.cursor.update(data={self._fields[2] : value}, clause=nclause)
                    else:
                        idata = dict(zip(self._fields, [section, name, value]))
                        if self._mainclause:
                            idata[self._mainclause.left] = self._mainclause.right
                        self.cursor.insert(data=idata)
                    if self.has_section(section):
                        for name, value in self.items(section):
                            if not newconfig.has_option(section, name):
                                clause = sclause & Eq(self._fields[1], name)
                                #print 'dclause', clause
                                self.cursor.delete(clause=clause)
                                
                        

class DefaultEnvironment(VariablesConfig):
    def __init__(self, conn):
        VariablesConfig.__init__(self, conn, 'default_environment',
                                 'section', option='option')
        
class CurrentEnvironment(VariablesConfig):
    def __init__(self, conn):
        VariablesConfig.__init__(self, conn, 'current_environment',
                                 'hostname', option='name')
        

class Differ(object):
    def __init__(self, left='', right=''):
        self.ldata = left
        self.rdata = right
        self.lpath = self.__createfile__(self.ldata, 'left')
        self.rpath = self.__createfile__(self.rdata, 'right')
        
    def diff(self):
        os.system('xxdiff %s %s' % (self.lpath, self.rpath))
        
    def __createfile__(self, data, name):
        tmp, path = tempfile.mkstemp('differ', name)
        tmp = file(path, 'w')
        tmp.write(data)
        tmp.close()
        return path

    def get_data(self, name=None):
        if name == 'left':
            left = file(self.lpath).read()
            return left
        elif name == 'right':
            right = file(self.rpath).read()
            return right
        elif name is None:
            left = file(self.lpath).read()
            right = file(self.rpath).read()
            return left, right
        else:
            raise Error, 'bad name %s' % name
        
    def isdifferent(self, name, data=None):
        if name == 'left':
            if data is None:
                data = self.get_data(name)
            return data == self.ldata
        if name == 'right':
            if data is None:
                data = self.get_data(name)
            return data == self.rdata
        else:
            raise Error, 'bad name %s' % name
            
if __name__ == '__main__':
    c = PaellaConnection()
    #tp = TraitParent(c, 'woody')
    #pp = TraitPackage(c, 'woody')
    #ct = ConfigTemplate()
    #p = Parser('var-table.csv')
    vc = VariablesConfig(c, 'family_environment', 'trait',
                         'family', 'test2')
    
