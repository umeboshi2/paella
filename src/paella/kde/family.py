from qt import SIGNAL

from kdeui import KMessageBox
from kdeui import KStdAction
from kdeui import KPopupMenu
from kdeui import KListViewItem

from paella.db.family import Family

from useless.kdebase import get_application_pointer
from useless.kdebase.mainwin import BaseSplitWindow

from paella.kde.base import split_url
from paella.kde.base.viewbrowser import ViewBrowser
from paella.kde.base.mainwin import BasePaellaWindow
from paella.kde.docgen.family import FamilyDoc

class FamilyView(ViewBrowser):
    def __init__(self, parent):
        ViewBrowser.__init__(self, parent, FamilyDoc)
        self.app = get_application_pointer()
        self.conn = self.app.conn
        self.family = Family(self.conn)

    def set_family(self, family):
        self.doc.set_family(family)
        self.setText(self.doc.output())
        self.family.set_family(family)

    def setSource(self, url):
        action, context, ident = split_url(url)
        if action == 'edit':
            config = self.family.getVariablesConfig(self.family.current)
            newconfig = config.edit()
            config.update(newconfig)
            self.set_family(ident)
        else:
            KMessageBox.error(self, 'action %s unimpletmented' % url)
    

class FamilyMainWindow(BaseSplitWindow, BasePaellaWindow):
    def __init__(self, parent):
        BaseSplitWindow.__init__(self, parent, FamilyView,
                                 name='FamilyMainWindow')
        self.initPaellaCommon()
        self.initActions()
        self.initMenus()
        self.initToolbar()
        self.cursor = self.conn.cursor(statement=True)
        self.family = Family(self.conn)
        self.refreshListView()
        self.resize(600, 800)
        self.setCaption('Paella Families')

    def initActions(self):
        collection = self.actionCollection()
        self.quitAction = KStdAction.quit(self.close, collection)
        self.newFamilyAction = KStdAction.openNew(self.newFamily, collection)
        self.importFamilyAction = KStdAction.open(self.slotImportFamily, collection)
        self.exportFamilyAction = KStdAction.saveAs(self.slotExportFamily, collection)
        
    def initMenus(self):
        mainmenu = KPopupMenu(self)
        menubar = self.menuBar()
        menubar.insertItem('&Main', mainmenu)
        menubar.insertItem('&Help', self.helpMenu(''))
        self.newFamilyAction.plug(mainmenu)
        self.importFamilyAction.plug(mainmenu)
        self.exportFamilyAction.plug(mainmenu)
        self.quitAction.plug(mainmenu)

    def initToolbar(self):
        toolbar = self.toolBar()
        self.newFamilyAction.plug(toolbar)
        self.importFamilyAction.plug(toolbar)
        self.exportFamilyAction.plug(toolbar)
        self.quitAction.plug(toolbar)

    def initlistView(self):
        self.listView.setRootIsDecorated(False)
        self.listView.addColumn('family')

    def refreshListView(self):
        self.listView.clear()
        for row in self.family.family_rows():
            item = KListViewItem(self.listView, row.family)
            item.family = row.family

    def selectionChanged(self):
        item = self.listView.currentItem()
        self.mainView.set_family(item.family)

    def newFamily(self):
        raise NotImplementedError, 'need to implement FamilyMainWindow.newFamily'

    def insertNewFamily(self):
        raise NotImplementedError, 'need to implement FamilyMainWindow.insertNewFamily'
    
    def slotImportFamily(self):
        KMessageBox.information(self, 'Import unimplemented')

    def slotExportFamily(self):
        KMessageBox.information(self, 'Export unimplemented')
        
        
