import os
from qt import SLOT, SIGNAL, Qt
from kdeui import KMainWindow
from kdeui import KPopupMenu
from kdeui import KMessageBox, KTextEdit
from kdeui import KListView, KListViewItem
from kdeui import KStdAction

from useless.db.midlevel import StatementCursor
from useless.kbase.gui import MainWindow, SimpleSplitWindow
from useless.kbase.gui import ViewWindow
from useless.kbase.gui import SimpleRecordDialog
from useless.kdb.gui import ViewBrowser

from paella.base import PaellaConfig
from paella.db import PaellaConnection
from paella.db.family import Family
from paella.kde.xmlgen import FamilyDoc

class SimpleEdit(KTextEdit):
    def __init__(self, app, parent):
        KTextEdit.__init__(self, parent)
        self.app = app
        
class FamilyView(ViewBrowser):
    def __init__(self, app, parent):
        ViewBrowser.__init__(self, app, parent, FamilyDoc)
        self.family = Family(self.app.conn)
        
    def set_family(self, family):
        self.doc.set_family(family)
        self.setText(self.doc.toxml())
        self.family.set_family(family)
        
    def setSource(self, url):
        action, context, id = str(url).split('.')
        if action == 'show':
            if context == 'parent':
                win = TraitMainWindow(self.app, self.parent(), self.doc.suite)
                win.view.set_trait(id)
            elif context == 'template':
                fid = id.replace(',', '.')
                package, template = fid.split('...')
                win = ViewWindow(self.app, self.parent(), SimpleEdit, 'TemplateView')
                templatefile = self.doc.trait._templates.templatedata(package, template)
                win.view.setText(templatefile)
                win.resize(600, 800)
            elif context == 'script':
                scriptfile = self.doc.trait._scripts.scriptdata(id)
                win = ViewWindow(self.app, self.parent(), SimpleEdit, 'ScriptView')
                win.view.setText(scriptfile)
                win.resize(600, 800)
        elif action == 'edit':
            #KMessageBox.information(self, 'edit the family %s ' % id)
            config = self.family.getVariablesConfig(self.family.current)
            newconfig = config.edit()
            config.update(newconfig)
            self.set_family(id)
            
                
        else:
            KMessageBox.information(self, 'called %s' % url)
        
        
class FamilyMainWindow(SimpleSplitWindow):
    def __init__(self, app, parent):
        SimpleSplitWindow.__init__(self, app, parent, FamilyView, 'FamilyMainWindow')
        self.app = app
        self.initActions()
        self.initMenus()
        self.initToolbar()
        self.conn = app.conn
        self.cfg = app.cfg
        self.cursor = StatementCursor(self.conn)
        self.family = Family(self.conn)
        self.refreshListView()
        self.resize(600, 800)
        self.setCaption('paella families')
        
    def initActions(self):
        collection = self.actionCollection()
        self.quitAction = KStdAction.quit(self.close, collection)
        self.newFamilyAction = KStdAction.openNew(self.newFamily, collection)
        
    def initMenus(self):
        mainMenu = KPopupMenu(self)
        menus = [mainMenu]
        self.menuBar().insertItem('&Main', mainMenu)
        self.menuBar().insertItem('&Help', self.helpMenu(''))
        self.newFamilyAction.plug(mainMenu)
        self.quitAction.plug(mainMenu)
        
    def initToolbar(self):
        toolbar = self.toolBar()
        self.newFamilyAction.plug(toolbar)
        self.quitAction.plug(toolbar)
        
    def initlistView(self):
        self.listView.setRootIsDecorated(True)
        self.listView.addColumn('group')
        
    def refreshListView(self):
        self.listView.clear()
        for row in self.family.family_rows():
            item = KListViewItem(self.listView, row.family)
            item.family = row.family

    def selectionChanged(self):
        current = self.listView.currentItem()
        if hasattr(current, 'family'):
            self.view.set_family(current.family)
        if hasattr(current, 'trait'):
            print 'trait is', current.trait
            self.view.set_trait(current.trait)
        if hasattr(current, 'suite'):
            print 'suite is', current.suite
            if hasattr(current, 'widget'):
                print 'widget is', current.widget

    def newFamily(self):
        dialog = SimpleRecordDialog(self, ['family'])
        dialog.connect(dialog, SIGNAL('okClicked()'), self.insertNewFamily)
        self._dialog = dialog

    def insertNewFamily(self):
        dialog = self._dialog
        data = dialog.getRecordData()
        family = data['family']
        if family not in self.family.all_families():
            self.family.create_family(family)
        else:
            KMessageBox.information(self, '%s already exists.' % family)
        self.refreshListView()
        
if __name__ == '__main__':
    cfg = PaellaConfig()
    conn = PaellaConnection(cfg)
    t = Trait(conn, suite='kudzu')
