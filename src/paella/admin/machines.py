from paella.db.midlevel import StatementCursor
from paella.sqlgen.clause import Eq
from paella.profile.base import Suites
from paella.profile.trait import Trait
from paella.gtk.middle import ListNoteBook, ScrollCList
from paella.gtk.windows import CommandBoxWindow
from paella.gtk.helpers import HasDialogs, make_menu, HasListbox
from paella.gtk import dialogs
from paella.dbgtk.base import TableEditor, BrowserWin
from paella.dbgtk.simple import RelationalBrowser

from gtk import ScrolledWindow


TRAITCMDS = ['import', 'export']
class MountsWin(TableEditor):
    def __init__(self, conn):
        cdata = dict(new='new mount', edit='edit mount')
        fields = ['mnt_point', 'fstype', 'mnt_opts', 'dump', 'pass']
        TableEditor.__init__(self, conn, 'mounts', 'mnt_name', fields, command_data=cdata)
        self.set_size_request(550, 250)
        
class KernelsWin(TableEditor):
    def __init__(self, conn):
        TableEditor.__init__(self, conn, 'kernels', 'kernel', [])
        self.set_size_request(150, 200)
        
class FsWin(BrowserWin):
    def __init__(self, conn):
        browser = RelationalBrowser(conn, 'filesystems', 'filesystem_mounts',
                                         'filesystem', ['mnt_name', 'ord', 'partition'])
        BrowserWin.__init__(self, conn, browser)

class DiskWin(BrowserWin):
    def __init__(self, conn):
        browser = RelationalBrowser(conn, 'disks', 'partitions',
                                         'diskname', ['partition', 'start', 'size', 'id'])
        BrowserWin.__init__(self, conn, browser)

class MachineTypesWin(BrowserWin):
    def __init__(self, conn):
        browser = RelationalBrowser(conn, 'machine_types', 'machine_disks',
                                         'machine_type', ['diskname', 'device'])
        BrowserWin.__init__(self, conn, browser)
        
class MachinesWin(TableEditor):
    def __init__(self, conn):
        cdata = dict(new='new machine', edit='edit a machine')
        fields = ['machine_type', 'kernel', 'profile', 'filesystem']
        TableEditor.__init__(self, conn, 'machines', 'machine', fields, cdata)
        self.set_size_request(550, 200)
        self.set_title('Edit the Machines')

class MainMachineWin(CommandBoxWindow):
    def __init__(self, conn):
        CommandBoxWindow.__init__(self)
        self.tbar.set_orientation('vertical')
        self.conn = conn
        commands = ['machines', 'machine types', 'filesystems', 'disks',
                    'mounts', 'kernels']
        for c in commands:
            self.tbar.add_button(c, c, self.toolbar_button_pressed)
            
    def toolbar_button_pressed(self, button, data):
        if data == 'machines':
            MachinesWin(self.conn)
        elif data == 'filesystems':
            FsWin(self.conn)
        elif data == 'machine types':
            #dialogs.Message('not ready yet')
            MachineTypesWin(self.conn)
        elif data == 'disks':
            DiskWin(self.conn)
        elif data == 'mounts':
            MountsWin(self.conn)
        elif data == 'kernels':
            KernelsWin(self.conn)
        else:
            dialogs.Message('unhandled command %s' % data)
            
        
if __name__ == '__main__':
    from paella.profile.base import PaellaConfig, PaellaConnection
    from gtk import mainloop, mainquit
    from gtk import glade
    gpath = '/home/umeboshi/Projects/paella/paella.glade'
    #xml = glade.XML(gpath)
    cfg = PaellaConfig()
    conn = PaellaConnection(cfg)
    win = MainMachineWin(conn)
    win.connect('destroy', mainquit)
    #dialogs.RecordEntry('hello there', [('a', 'dd'), ('b', 'bb'), ('c', 'cc')])
    mainloop()
    
        
