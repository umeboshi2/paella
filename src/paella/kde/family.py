import os
from qt import SLOT, SIGNAL, Qt
from kdeui import KMainWindow
from kdeui import KPopupMenu
from kdeui import KMessageBox, KTextEdit
from kdeui import KListView, KListViewItem

from paella.profile.base import PaellaConfig
from paella.profile.base import PaellaConnection
from paella.profile.family import Family

from kommon.pdb.midlevel import StatementCursor
from kommon.base.gui import MainWindow, SimpleSplitWindow
from kommon.base.gui import ViewWindow
from kommon.db.gui import ViewBrowser
from paella.kde.xmlgen import FamilyDoc

class SimpleEdit(KTextEdit):
    def __init__(self, app, parent):
        KTextEdit.__init__(self, parent)
        self.app = app
        
class FamilyView(ViewBrowser):
    def __init__(self, app, parent):
        ViewBrowser.__init__(self, app, parent, FamilyDoc)

    def set_family(self, family):
        self.doc.set_family(family)
        self.setText(self.doc.toxml())

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
        
    def initMenus(self):
        mainMenu = KPopupMenu(self)
        menus = [mainMenu]
        self.menuBar().insertItem('&Main', mainMenu)
        self.menuBar().insertItem('&Help', self.helpMenu(''))

    def initToolbar(self):
        toolbar = self.toolBar()

    def initlistView(self):
        self.listView.setRootIsDecorated(True)
        self.listView.addColumn('group')
        
    def refreshListView(self):
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


if __name__ == '__main__':
    cfg = PaellaConfig()
    conn = PaellaConnection(cfg)
    t = Trait(conn, suite='kudzu')
