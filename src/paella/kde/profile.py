import os
from qt import SLOT, SIGNAL, Qt
from qt import QListBoxText
from qt import QFrame, QVBoxLayout, QHBoxLayout

from kdeui import KMainWindow
from kdeui import KPopupMenu
from kdeui import KMessageBox, KTextEdit
from kdeui import KListView, KListViewItem
from kdeui import KActionSelector
from kdeui import KPushButton

from paella.profile.base import PaellaConfig
from paella.profile.base import PaellaConnection
from paella.profile.trait import Trait
from paella.profile.profile import Profile

from kommon.pdb.midlevel import StatementCursor
from kommon.base.gui import MainWindow, SimpleSplitWindow
from kommon.base.gui import ViewWindow
from kommon.base.gui import BaseAssigner
from kommon.db.gui import ViewBrowser
from paella.kde.xmlgen import ProfileDoc

class SimpleEdit(KTextEdit):
    def __init__(self, app, parent):
        KTextEdit.__init__(self, parent)
        self.app = app

class TraitAssigner(BaseAssigner):
    def __init__(self, app, parent, profile):
        self.profile = Profile(app.conn)
        self.profile.set_profile(profile)
        BaseAssigner.__init__(self, app, parent,
                              name='TraitAssigner', udbuttons=True)
        
    def initView(self):
        app = self.app
        self.db = app.db
        self.suite = self.profile.current.suite
        self.traits = StatementCursor(app.conn)
        self.traits.set_table('%s_traits'  % self.suite)
        
        ptrows = self.profile.get_trait_rows()
        pt = [r.trait for r in ptrows]
        all_trows = self.traits.select(fields=['trait'], order=['trait'])
        trows = [r for r in all_trows if r.trait not in pt]
        abox = self.listBox.availableListBox()
        sbox = self.listBox.selectedListBox()
        for row in ptrows:
            QListBoxText(sbox, row.trait)
        for row in trows:
            QListBoxText(abox, row.trait)

class TraitAssignerOrig(KMainWindow):
    def __init__(self, app, parent, profile):
        KMainWindow.__init__(self, parent, 'TraitAssigner')
        self.page = QFrame(self)
        self.vbox = QVBoxLayout(self.page, 5, 7)
        self.listBox = KActionSelector(self.page)
        self.listBox.setShowUpDownButtons(True)
        self.setCentralWidget(self.page)
        self.vbox.addWidget(self.listBox)
        hbox = QHBoxLayout(self.page, 5, 7)
        self.vbox.addLayout(hbox)
        self.ok_button = KPushButton('ok', self.page)
        self.cancel_button = KPushButton('cancel', self.page)
        hbox.addWidget(self.ok_button)
        hbox.addWidget(self.cancel_button)
        self.app = app
        self.db = app.db
        self.profile = Profile(app.conn)
        self.profile.set_profile(profile)
        self.suite = self.profile.current.suite
        self.traits = StatementCursor(app.conn)
        self.traits.set_table('%s_traits'  % self.suite)
        self.initlistView()
        self.show()

    def initlistView(self):
        ptrows = self.profile.get_trait_rows()
        pt = [r.trait for r in ptrows]
        all_trows = self.traits.select(fields=['trait'], order=['trait'])
        trows = [r for r in all_trows if r.trait not in pt]
        abox = self.listBox.availableListBox()
        sbox = self.listBox.selectedListBox()
        for row in ptrows:
            QListBoxText(sbox, row.trait)
        for row in trows:
            QListBoxText(abox, row.trait)
            
        
class ProfileView(ViewBrowser):
    def __init__(self, app, parent):
        ViewBrowser.__init__(self, app, parent, ProfileDoc)

    def set_profile(self, profile):
        self.doc.set_profile(profile)
        self.setText(self.doc.toxml())

    def set_suite(self, suite):
        self.doc.suite = suite
        self.doc.trait = Trait(self.app.conn, suite=suite)

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
            if context == 'traits':
                win = TraitAssigner(self.app, self.parent(), id)
            else:
                self._url_error(url)
                
        else:
            KMessageBox.information(self, 'called %s' % url)
        
        
class ProfileMainWindow(SimpleSplitWindow):
    def __init__(self, app, parent):
        SimpleSplitWindow.__init__(self, app, parent, ProfileView, 'ProfileMainWindow')
        self.app = app
        self.initActions()
        self.initMenus()
        self.initToolbar()
        self.conn = app.conn
        self.cfg = app.cfg
        self.cursor = StatementCursor(self.conn)
        self.profile = Profile(self.conn)
        self.refreshListView()
        self.resize(600, 800)
        self.setCaption('paella profiles')
        
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
        for row in self.profile.select(fields=['profile', 'suite'], order='profile'):
            item = KListViewItem(self.listView, row.profile)
            item.profile = row.profile
                
    def selectionChanged(self):
        current = self.listView.currentItem()
        if hasattr(current, 'profile'):
            self.view.set_profile(current.profile)
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
