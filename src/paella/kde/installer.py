#from ConfigParser import RawConfigParser

from qt import SIGNAL, SLOT, Qt
#from qt import QWidget

from kdeui import KMainWindow, KPushButton
#from kdeui import KListView, KListViewItem
#from kdeui import KStdAction, KPopupMenu
#from kfile import KFileDialog

#from useless.sqlgen.clause import Eq
#from useless.db.midlevel import StatementCursor
from paella.db import DefaultEnvironment
from paella.db import CurrentEnvironment

from paella.kde.db.gui import dbwidget
#from paella.kde.base.actions import EditAction

ETYPE = { 'default' : DefaultEnvironment,
          'current' : CurrentEnvironment
          }

class InstallerManager(object):
    def __init__(self, conn):
        self.conn = conn
        self.defenv = DefaultEnvironment(conn)

    def get_known_machines(self):
        machines = []
        macs = self.defenv.options('machines')
        for mac in macs:
            machine = self.defenv.get('machines', mac)
            if machine not in machines:
                machines.append(machine)
        return machines

class InstallerMainWin(KMainWindow):
    def __init__(self, app, parent):
        KMainWindow.__init__(self, parent)
        dbwidget(self, app)

        self.mainView = KPushButton('hello there', self)
        self.setCentralWidget(self.mainView)
        self.setCaption('Installer Management')
        self.show()
        
