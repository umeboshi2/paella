from os.path import isfile, join, dirname
import shelve
from sets import Set
from threading import Thread
import csv
from Queue import Queue, Full, Empty

import pycurl

from paella.base import Error
from paella.base.util import blank_list, ujoin
from paella.base.util import makepaths

def hide(string):
    return '__%s__' % string

class DbRowDescription(list):
    def __init__(self, keys):
        list.__init__(self, keys)

    def sort(self):
        pass



class DbBaseRow(object):
    def __init__(self, desc, row):
        object.__init__(self)
        self._keylist_ = desc
        self._vallist_ = row
        #print desc, row
        self.__datadict__ = dict(zip(self._keylist_, self._vallist_))
        
    def keys(self):
        return self._keylist_

    def values(self):
        return self._vallist_

    def items(self):
        return zip(self._keylist_, self._vallist_)

    def __getitem__(self, key):
        if key in self._keylist_:
            return self.__datadict__[key]
        elif isinstance(key, int):
            return self._vallist_[key]
        else:
            raise Error, 'item not found'

    def __getattr__(self, key):
        if key in self._keylist_:
            return self.__datadict__[key]
        else:
            return getattr(self, key)
        
    def __len__(self):
        return len(self._keylist_)

    def __repr__(self):
        return str(self._vallist_)

class _Empty(DbBaseRow):
    def __init__(self, desc):
        DbBaseRow.__init__(self, desc, blank_list(len(desc)))



class Parser(list):
    def __init__(self, path, field_sep='\t'):
        csvfile = file(path)
        parser = csv.reader(csvfile, field_sep=field_sep)
        rows = [parser.parse(line) for line in csvfile.readlines()]
        csvfile.close()
        self.fields = rows[0]
        for row in rows[1:]:
            if len(row):
                self.append(DbBaseRow(self.fields, row))


class SuperDict(object):
    def __init__(self, main_keys, keyfunction, valfunction):
        self.main_values = main_keys
        self.__keyfunction__ = keyfunction
        self.__valfunction__ = valfunction
        self.__make_superdict__()
        
    def __getitem__(self, key):
        if key not in self.__superdict__:
            raise Error, 'key %s not in SuperDict' % key
        main, field = self.__superdict__[key]
        return self.get(main, field)
    
    def __setitem__(self, key, value):
        if key not in self.__superdict__:
            raise Error, 'SuperDict cant make new items'
        main, field = self.__superdict__[key]
        self.set(main, field, value)

    def get(self, main, field):
        return self.__valfunction__('get', main, field)

    def set(self, main, field, value):
        self.__valfunction__('set', main, field, value)

    def keys(self):
        return self.__superdict__.keys()

    def values(self):
        return [self[key] for key in self.keys()]
    

    def items(self):
        return [(key, self[key]) for key in self.keys()]

    def __contains__(self, key):
        return key in self.__superdict__
    
    def __make_superdict__(self):
        self.__superdict__ = {}
        for field in self.main_values:
            for key in self.__keyfunction__(field):
                self.__superdict__[ujoin(field, key)] = (field, key)

class SimpleSuper(SuperDict):
    def __init__(self):
        self.__main_dict__ = {}
        SuperDict.__init__(self, [],
                           self._simple_keyfunction_,
                           self._simple_valfunction_)

    def insert_main(self, value):
        self.main_values = self.__main_dict__.keys()
        if value not in self.main_values:
            self.__main_dict__[value] = {}
            self.remake()
            
    def insert_field(self, main, field, value=None):
        if field not in self.main_values:
            self.__main_dict__[main][field] = value
            self.remake()
            
    def remake(self):
        self.main_values = self.__main_dict__.keys()
        self.__make_superdict__()

    def _simple_keyfunction_(self, main):
        return self.__main_dict__[main].keys()

    def _simple_valfunction_(self, action, main, field, value=None):
        if action == 'get':
            return self.__main_dict__[main][field]
        elif action == 'set':
            self.__main_dict__[main][field] = value
            
    
            

class SuperShelf(shelve.DbfilenameShelf):
    def __init__(self, dbpath, initfunc, flag='r'):
        if not isfile(dbpath):
            shelve.DbfilenameShelf.__init__(self, dbpath, 'n')
            initfunc()
        else:
            shelve.DbfilenameShelf.__init__(self, dbpath, flag)

    def __init_new_db__(self):
        self['___fields___'] = []
        self['___orders___'] = {}
        self['___order_keys___'] = {}
        self['___field_keys___'] = {}
        
    def insert_field(self, name):
        fields = self['___fields___']
        fieldkeys = self['___field_keys___']
        fields.append(name)
        fieldkeys[name] = Set()
        self['___fields___'] = fields
        self['___field_keys___'] = fieldkeys
        
    def insert_order(self, order, fieldlist):
        fields = self['___fields___']
        orders = self['___orders___']
        orderkeys = self['___order_keys___']
        for field in fieldlist:
            if field not in fields:
                raise Error, 'bad field %s in order' % field
        orders[order] = fieldlist
        self['___orders___'] = orders
        orderkeys[order] = []
        self['___order_keys___'] = orderkeys

    def insert_item(self, order, fields, value):
        fieldkeys = self['___field_keys___']
        orders = self['___orders___']
        for k,v in zip(orders[order], fields):
            fieldkeys[k].add(v)
        fullkey = ujoin(*fields)
        self[fullkey] = value
        self['___field_keys___'] = fieldkeys
    def get_value(self, keys):
        return self[ujoin(*keys)]
        

    def fieldkeys(self, field):
        fieldkeys = self['___field_keys___']
        return list(fieldkeys[field])

    def items(self, order):
        keys = self.keys(order)
        return [(k, self.get_value(order, k)) for k in keys]

class DownloadJob(object):
    def __init__(self, url, path):
        object.__init__(self)
        self.url = url
        self.path = path
        

class DownloadThread(Thread):
    def __init__(self, url, path, progress_function):
        Thread.__init__(self)
        self.file = file(path, 'w')
        self.progress = progress_function
        self.curl = pycurl.Curl()
        self.url = url
        c = self.curl
        c.setopt(c.URL, self.url)
        c.setopt(c.WRITEFUNCTION, self.file.write)
        c.setopt(c.MAXREDIRS, 5)
        c.setopt(c.FOLLOWLOCATION, 1)
        c.setopt(c.NOPROGRESS, 0)
        c.setopt(c.PROGRESSFUNCTION, self.progress)
        c.setopt(c.NOSIGNAL, 1)

    def run(self):
        self.curl.perform()
        self.curl.close()
        self.file.close()
        self.progress(1, 1, 0, 0)

class DownloadQueue(Queue):
    def __init__(self, maxsize=0):
        Queue.__init__(self, maxsize)

    def put(self, url, path):
        Queue.put(self, DownloadJob(url, path))

class DlWorker(Thread):
    def __init__(self, queue, progress_function, url_function):
        Thread.__init__(self)
        self.curl = pycurl.Curl()
        self.jobs = queue
        self.progress = progress_function
        self.urlfun = url_function
        c = self.curl
        c.setopt(c.MAXREDIRS, 5)
        c.setopt(c.FOLLOWLOCATION, 1)
        c.setopt(c.NOPROGRESS, 0)
        c.setopt(c.PROGRESSFUNCTION, self.progress)
        c.setopt(c.NOSIGNAL, 1)

    def run(self):
        c = self.curl
        while True:
            try:
                self.current_job = self.jobs.get()
            except Empty:
                self.current_job = None
            else:
                if self.current_job is not None:
                    c.setopt(c.URL, self.current_job.url)
                    self.urlfun(self.current_job.url)
                    try:
                        f = file(self.current_job.path, 'w')
                    except IOError:
                        makepaths(dirname(self.current_job.path))
                        f = file(self.current_job.path, 'w')
                    c.setopt(c.WRITEFUNCTION, f.write)
                    c.perform()
                    f.close()
                    self.progress(1, 1, 0, 0)
                    self.current_job = None
                else:
                    pass
                
                
class DownloadPool(object):
    def __init__(self, maxthreads=3):
        object.__init__(self)
        self.threads = []
        self.queue = DownloadQueue()
        for i in range(maxthreads):
            thread = DlWorker(self.queue, self.progress)
            thread.start()
            self.threads.append(thread)

    def put(self, url, path):
        self.queue.put(url, path)
        
        

if __name__ == '__main__':
    ss = SuperShelf('testit.db')
    
    
