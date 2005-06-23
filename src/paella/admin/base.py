import os, sys
from os.path import join, dirname

from useless.gtk import dialogs
from useless.gtk.middle import ScrollCList
from useless.gtk.windows import MenuWindow

from gtk import FileSelection
from gtk import mainloop, mainquit

from useless.base import Error, debug
from useless.base.tarball import RootTarball
from useless.base.util import get_sub_path

from useless.db.lowlevel import QuickConn
from useless.db.midlevel import StatementCursor


from paella.profile.base import PaellaConfig

class SystemTar(object):
    def __init__(self, conn, cfg):
        object.__init__(self)
        self.conn = conn
        self.cfg = cfg


    def set_tarfile(self, path):
        self.tar = RootTarball(path)
        self.tar.fake_extract()
        
    
        

class SystemTarWindow(FileSelection):
    def __init__(self, name='SystemTarWindow', **kw):
        FileSelection.__init__(self, **kw)
        self.cfg = PaellaConfig()
        self.dialogs = {}.fromkeys(['dbname', 'traits', 'templates'])
        self.tar = SystemTar(None, self.cfg)
        self.show()
        
    def set_filename(self, path):
        self.tar.set_tarfile(path)
        FileSelection.set_filename(self, self.tar.tar.tmpdir + '/')

    def extract_file(self):
        path = self.get_filename()
        spath = get_sub_path(path, self.tar.tar.tmpdir)
        info = self.tar.tar.getmember(spath)
        return info, self.tar.tar.extractfile(info)


def select_from_tarfile(action, path, ok_function):
        filesel = SystemTarWindow(title='__select_a_file__')
        filesel.cancel_button.connect('clicked',
                                      lambda x: filesel.destroy())
        filesel.ok_button.connect('clicked', ok_function, filesel)
        filesel.set_data('action', action)
        filesel.set_filename(path)
        return filesel

if __name__ == '__main__':
    win = SystemTarWindow()
    win.connect('destroy', mainquit)
    path = os.path.join(cfg['bkuptarball_path'], 'simplestable.tar')
    win.set_filename(path)
    mainloop()
    
        
