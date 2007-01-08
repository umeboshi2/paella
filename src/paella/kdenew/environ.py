from ConfigParser import RawConfigParser

from qt import SIGNAL

from kdeui import KListView, KListViewItem
from kdeui import KStdAction
from kdeui import KPopupMenu

from kfile import KFileDialog

from useless.sqlgen.clause import Eq

from paella.db import DefaultEnvironment
from paella.db import CurrentEnvironment

from useless.kdebase import get_application_pointer

from paella.kdenew.base.mainwin import BasePaellaWindow
from paella.kdenew.base.actions import EditAction

ETYPE = { 'default' : DefaultEnvironment,
          'current' : CurrentEnvironment
          }


class EnvironmentList(KListView):
    def __init__(self, parent, etype='default', name='EnvironmentList'):
        KListView.__init__(self, parent, name)
        self.app = get_application_pointer()
        self.conn = self.app.conn
        self.etype = etype
        self.environ = ETYPE[self.etype](self.conn)
        self.cursor = self.conn.cursor(statement=True)
        self.cursor.set_table('%s_environment' % self.etype)
        self.setRootIsDecorated(True)
        for field in ['section', 'option', 'value']:
            self.addColumn(field)

    def refreshListView(self):
        self.clear()
        if self.etype == 'default':
            fields = ['section', 'option', 'value']
        elif self.etype == 'current':
            fields = ['hostname', 'name', 'value']
        else:
            raise ValueError, "%s is a bad environment type" % self.etype
        rows = self.cursor.select(fields=fields, order=fields[:2])
        for row in rows:
            KListViewItem(self, *row)

    def file_selected(self, filesel):
        filename = str(filesel.selectedFile())
        print filename, filesel.actiontype
        action = filesel.actiontype
        if action == 'save':
            self.environ.write(file(filename, 'w'))
        elif action == 'load':
            newcfg = RawConfigParser()
            newcfg.read(filename)
            self._update_environ(newcfg)
        else:
            raise ValueError, 'bad action %s' % action

    def _update_environ(self, newcfg):
        self.environ.update(newcfg)
        self.environ = ETYPE[self.etype](self.conn)
        self.refreshListView()

    def slotEdit(self):
        newcfg = self.environ.edit()
        self._update_environ(newcfg)

class EnvironmentWindow(BasePaellaWindow):
    def __init__(self, parent, etype):
        BasePaellaWindow.__init__(self, parent, name='EnvironmentWindow')
        self.initPaellaCommon()
        self.mainView = EnvironmentList(self, etype)
        self.initActions()
        self.initMenus()
        self.initToolbar()
        self.setCentralWidget(self.mainView)
        self.mainView.refreshListView()
        self.resize(600, 500)
        self.setCaption('%s Environment' % etype.capitalize())

    def initActions(self):
        collection = self.actionCollection()
        self.loadAction = KStdAction.open(self.slotLoad, collection)
        self.editAction = EditAction(self.mainView.slotEdit, collection)
        self.saveAction = KStdAction.save(self.slotSave, collection)
        self.quitAction = KStdAction.quit(self.close, collection)

    def initMenus(self):
        mainmenu = KPopupMenu(self)
        menubar = self.menuBar()
        menubar.insertItem('&Main', mainmenu)
        menubar.insertItem('&Help', self.helpMenu(''))
        actions = [self.loadAction, self.editAction,
                   self.saveAction, self.quitAction]
        for action in actions:
            action.plug(mainmenu)

    def initToolbar(self):
        toolbar = self.toolBar()
        actions = [self.loadAction, self.editAction,
                   self.saveAction, self.quitAction]
        for action in actions:
            action.plug(toolbar)

    def slotLoad(self):
        self._slotFileio('load')

    def slotSave(self):
        self._slotFileio('save')

    def _slotFileio(self, actiontype):
        filesel = KFileDialog('.', '', self, '%sEnvironment' % actiontype.upper(), True)
        filesel.actiontype = actiontype
        self.connect(filesel, SIGNAL('okClicked()'), self.file_selected)
        filesel.show()
        self.filesel = filesel

    def file_selected(self):
        self.mainView.file_selected(self.filesel)
        
