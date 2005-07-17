from ConfigParser import RawConfigParser

from qt import SIGNAL, SLOT, Qt
from qt import QWidget

from kdeui import KMainWindow, KPushButton
from kdeui import KListView, KListViewItem
from kdeui import KStdAction, KPopupMenu
from kfile import KFileDialog

from paella.sqlgen.clause import Eq
from paella.db.midlevel import StatementCursor
from paella.profile.base import DefaultEnvironment
from paella.profile.base import CurrentEnvironment

from paella.kde.db.gui import dbwidget
from paella.kde.base.actions import EditAction

ETYPE = { 'default' : DefaultEnvironment,
          'current' : CurrentEnvironment
          }

class EnvironmentList(KListView):
    def __init__(self, app, parent, etype='default', name='EnvironmentList'):
        KListView.__init__(self, parent, name)
        dbwidget(self, app)
        self.etype = etype
        self.environ = ETYPE[self.etype](self.conn)
        self.cursor = StatementCursor(self.conn)
        self.cursor.set_table('%s_environment' % self.etype)
        self.setRootIsDecorated(True)
        for field in ['section', 'option', 'value']:
            self.addColumn(field)

    def refreshlistView(self):
        self.clear()
        if self.etype == 'default':
            fields = ['section', 'option', 'value']
            rows = self.cursor.select(fields=fields, order=['section', 'option'])
        if self.etype == 'current':
            fields = ['hostname', 'name', 'value']
            rows = self.cursor.select(fields=fields, order=['hostname', 'name'])
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
        
    def _update_environ(self, newcfg):
        self.environ.update(newcfg)
        self.environ = ETYPE[self.etype] (self.conn)
        self.refreshlistView()
        
    def slotEdit(self):
        newcfg = self.environ.edit()
        self._update_environ(newcfg)
        
class DefEnvWin(KMainWindow):
    def __init__(self, app, parent, etype):
        KMainWindow.__init__(self, parent)
        #self.app = app
        dbwidget(self, app)
        
        self.mainView = EnvironmentList(self.app, self, etype)
        self.initActions()
        self.initMenus()
        self.initToolbar()

        self.setCentralWidget(self.mainView)
        self.mainView.refreshlistView()
        self.resize(600, 500)
        self.show()
        

    def initActions(self):
        collection = self.actionCollection()
        self.loadAction = KStdAction.open(self.slotLoad, collection)
        #self.editAction = KStdAction.replace(self.mainView.slotEdit, collection)
        self.editAction = EditAction(self.mainView.slotEdit, collection)
        self.saveAction = KStdAction.save(self.slotSave, collection)
        self.quitAction = KStdAction.quit(self.close, collection)
       
    def initMenus(self):
        mainMenu = KPopupMenu(self)
        menus = [mainMenu]
        self.menuBar().insertItem('&Main', mainMenu)
        self.menuBar().insertItem('&Help', self.helpMenu(''))
        actions = [self.loadAction, self.editAction,
                   self.saveAction,
                   self.quitAction]
        for action in actions:
            action.plug(mainMenu)
            
    def initToolbar(self):
        print 'initToolbar'
        toolbar = self.toolBar()
        actions = [self.loadAction, self.editAction,
                   self.saveAction,
                   self.quitAction]
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
