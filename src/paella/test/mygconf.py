import os, os.path

from paella.gtk.dialogs import Dialog, CList, ScrollVBox, ScrollHBox
from paella.gtk.simple import ItemButton, ItemEntry
from paella.base.objects import DbRowDescription, DbBaseRow
from paella.db.lowlevel import LocalConnection, CommandCursor

from gtk import mainloop, mainquit, ScrolledWindow, VBox

import gconf
    
def get_entries(client, path):
    entries = client.all_entries(path)
    keylist = [os.path.basename(x.key) for x in entries]
    vals = [str(x.value) for x in entries]
    vals = []
    for x in entries:
        try:
            v = x.value.to_string()
        except AttributeError:
            v = 'THISISNONETYPE'
        vals.append(v)
    edict = dict(zip(keylist, vals))
    return edict

                
class _ClientNode(object):
    def __init__(self, client, path):
        object.__init__(self)
        self._gc_client = client
        self.dir = os.path.dirname(path)
        self.dirs = self._getdirs_(path)
        self.children = {}
        for d in self.dirs:
            if not len(self._getdirs_(d)):
                self.children[os.path.basename(d)] = self._getentries_(d)
            else:
                self.children[os.path.basename(d)] = _ClientNode(client, d)

    def _getdirs_(self, dir):
        return self._gc_client.all_dirs(dir)
    
    def _getentries_(self, dir):
        return get_entries(self._gc_client, dir)

    def __getitem__(self, key):
        return self.children[key]

    def items(self):
        return self.children.items()
    def keys(self):
        return self.children.keys()
    def values(self):
        return self.children.values()
    

class DirectoryWindow(CList):
    def __init__(self, client, path):
        CList.__init__(self, path)
        self._gc_client = client
        self._path_ = path
        #rows = self.__make_rows__(self._getdirs_(path))
        #print rows
        #self.set_rows(rows)
        self.set_rows(self._getdirs_(path), [path])
        self.set_row_select(self.make_new_window)
        self.add_button('go_up', self._go_up, label='go up')

    def _go_up(self, *args):
        ndir = os.path.dirname(self._path_)
        ndirs = self._getdirs_(ndir)
        self._reset_rows(ndir, ndirs)
        

    def _getdirs_(self, dir):
        return self._gc_client.all_dirs(dir)
    
    def __make_rows__2(self, dirs):
        return [{'dir':x} for x in dirs]
        
    def make_new_window(self, lbox, row, col, event):
        row = lbox.get_selected_data()
        ndir = row[0][0]
        ndirs = self._getdirs_(ndir)
        print 'ndirs is %s' %str(ndirs)
        if not len(ndirs):

            EntryWindow(self._gc_client, ndir)
        else:
            self._reset_rows(ndir, ndirs)
    def _reset_rows(self, ndir, ndirs):
        self._path_ = ndir
        self.label.set_text(ndir)
        #self.set_rows(self.__make_rows__(ndirs))
        self.set_rows(ndirs, [ndir])
        self.set_row_select(self.make_new_window)
        
class EntryWindow(ScrollVBox):
    def __init__(self, client, path):
        ScrollVBox.__init__(self, path)
        for i in get_entries(client, path).items():
            self.mbox.add(ItemEntry(i))
        self._gc_client = client
        self.set_usize(400,200)
        
def mycancel(*args):
    print args
    print 'cancelled'
    mainquit()

cl = gconf.client_get_default()

win = DirectoryWindow(cl, '/')
win.set_cancel(mycancel)
win.connect('destroy', mycancel)

mainloop()
c = _ClientNode(cl,'/')

cn = _ClientNode

def cn2str(cnode):
    foo = ''
    for k, v in cnode.items():
        if type(v) == str:
            foo += '\t%s: --> %s\n' %(k,v)
        else:
            foo += '%s:\n' %k
            foo += cn2str(v)
    return foo


f = file('gconfdump.txt','w')
f.write(cn2str(c))
f.close()
