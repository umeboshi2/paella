import os
from os.path import isdir, isfile, join, basename, dirname
from ConfigParser import RawConfigParser
from ConfigParser import ConfigParser
import tempfile

from useless.base import Error, NoExistError
from useless.base.util import ujoin, makepaths, md5sum, strfile
from useless.db.midlevel import StatementCursor
from useless.sqlgen.clause import Eq

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
    
class VariablesConfig(ConfigParser):
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
        ConfigParser.__init__(self)
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
                    v = str(self.get(section, k, raw=True)).replace('\n', '\n\t')
                    cfile.write('%s:\t%s\n' % (k, v))
            cfile.write('\n')
            
    def edit(self):
        tmp, path = tempfile.mkstemp('variables', 'config')
        tmp = file(path, 'w')
        self.write(tmp)
        tmp.close()
        os.system('$EDITOR %s' % path)
        tmp = file(path, 'r')
        newconfig = ConfigParser()
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
        lcfg, rcfg = ConfigParser(), ConfigParser()
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
            
