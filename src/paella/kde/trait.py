import os
import re
#import tempfile
import commands

from qt import SLOT, SIGNAL, Qt
from qt import QSyntaxHighlighter
from qt import QColor, QWidget
from qt import QVBoxLayout, QHBoxLayout
from qt import QSplitter
from qtext import QextScintilla, QextScintillaLexer
from qtext import QextScintillaLexerPython

from kdecore import KURL
from kdeui import KMainWindow
from kdeui import KPopupMenu, KStdAction
from kdeui import KMessageBox, KTextEdit
from kdeui import KListView, KListViewItem
from kfile import KFileDialog
from kio import KIO

from useless.base.template import Template

from paella.base import PaellaConfig
from paella.db import PaellaConnection
from paella.db.trait import Trait

from useless.db.midlevel import StatementCursor
from useless.kbase.gui import MainWindow, SimpleSplitWindow
from useless.kbase.gui import ViewWindow, SimpleRecordDialog
from useless.kdb.gui import ViewBrowser
from useless.kdb.gui import RecordSelector

from paella.kde.base import RecordSelectorWindow
#from paella.kde.xmlgen import TraitDoc, PackageDoc
from paella.kde.docgen.trait import TraitDoc, PackageDoc
from paella.kde.db.gui import dbwidget
#from paella.kde.differ import TraitList
from paella.kde.template import TemplateEditorWindow
from paella.kde.template import SimpleEdit

class AnotherView(QextScintilla):
    def __init__(self, app, parent):
        QextScintilla.__init__(self, parent)
        self.app = app
        self.pylex = QextScintillaLexerPython(self)
        self.lex = QextScintillaLexer(self)
        
    def setText(self, text):
        line = text.split('\n')[0]
        if 'python' in line:
            self.setLexer(self.pylex)
        else:
            self.setLexer(self.lex)
        QextScintilla.setText(self, text)

class PackageView(ViewBrowser):
    def __init__(self, app, parent):
        ViewBrowser.__init__(self, app, parent, PackageDoc)
        
class PackageSelector(RecordSelector):
    def __init__(self, app, parent, suite):
        table = '%s_packages' % suite
        fields = ['package', 'priority', 'section', 'installedsize',
                  'maintainer', 'version', 'description']
        idcol = 'package'
        groupfields = ['priority', 'section', 'maintainer']
        view = PackageView
        RecordSelector.__init__(self, app, parent, table, fields,
                                idcol, groupfields, view, 'PackageSelector')

class PackageSelectorWindow(KMainWindow):
    def __init__(self, app, parent, suite):
        KMainWindow.__init__(self, parent, 'PackageSelector')
        self.app = app
        self.conn = app.conn
        self.mainView = PackageSelector(self.app, self, suite)
        self.mainView.recView.doc.set_suite(suite)
        self.setCentralWidget(self.mainView)
        self.show()
        
class TraitView(ViewBrowser):
    def __init__(self, app, parent):
        ViewBrowser.__init__(self, app, parent, TraitDoc)

    def set_trait(self, trait):
        self.doc.set_trait(trait)
        self.setText(self.doc.output())

    def resetView(self):
        self.set_trait(self.doc.trait.current_trait)
        
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
            else:
                self._url_error(url)
        elif action == 'edit':
            if context == 'templates':
                #win = KFileDialog('.', '*', self, 'hello file dialog', False)
                #win.show()
                #win = TemplateEditorWindow(self.app, self.parent(), self.doc.suite)
                win = KFileDialog('.', '', self, 'SystemTarball', True)
                self.connect(win, SIGNAL('okClicked()'), self.fileSelected)
                win.show()
                self._dialog = win
                
            elif context == 'packages':
                win = PackageSelectorWindow(self.app, self.parent(), self.doc.suite)
            elif context == 'script':
                self.doc.trait.edit_script(id)
            elif context == 'template':
                fid = id.replace(',', '.')
                package, template = fid.split('...')
                self.doc.trait.edit_template(package, template)
            else:
                self._url_error(url)
        elif action == 'new':
            if context == 'package':
                win = SimpleRecordDialog(self, ['package', 'action'])
                win.connect(win, SIGNAL('okClicked()'), self.slotAddPackage)
                win.setRecordData(dict(action='install'))
                self._dialog = win
        else:
            self._url_error(url)

    def slotAddPackage(self):
        win = self._dialog
        data = win.getRecordData()
        self.doc.trait.add_package(data['package'], data['action'])
        self.resetView()

    def fileSelected(self):
        filesel = self._dialog
        filename = str(filesel.selectedFile())
        print filename
        filesel.close()
        filesel = KFileDialog('.', '', self, 'SystemTarball', True)
        url = 'tar://%s' % filename
        filesel.setURL(KURL(url))
        filesel.connect(filesel, SIGNAL('okClicked()'), self.newTemplateSelected)
        filesel.show()
        self._dialog = filesel
        
    def newTemplateSelected(self):
        filesel = self._dialog
        urlobj = filesel.selectedURL()
        url = urlobj.url()
        print 'selected url is', url
        data = commands.getoutput('kioexec cat %s' % url)
        print len(data), ' bytes of data copied'
        print data
        
    def slotGetFromTarDone(self, job):
        print 'got from tar', job, 'job'
        
    
class TraitMainWindow(SimpleSplitWindow):
    def __init__(self, app, parent, suite):
        SimpleSplitWindow.__init__(self, app, parent, TraitView, 'TraitMainWindow')
        self.app = app
        self.initActions()
        self.initMenus()
        self.initToolbar()
        self.conn = app.conn
        self.suite = suite
        self.cfg = app.cfg
        self.cursor = StatementCursor(self.conn)
        self.trait = Trait(self.conn, suite=suite)
        self.refreshListView()
        self.view.set_suite(suite)
        self.resize(600, 800)
        self.setCaption('%s traits' % suite)
        
    def initActions(self):
        collection = self.actionCollection()
        self.quitAction = KStdAction.quit(self.close, collection)
        self.newTraitAction = KStdAction.openNew(self.newTrait, collection)
        
    def initMenus(self):
        mainMenu = KPopupMenu(self)
        menus = [mainMenu]
        self.menuBar().insertItem('&Main', mainMenu)
        self.menuBar().insertItem('&Help', self.helpMenu(''))
        self.newTraitAction.plug(mainMenu)
        self.quitAction.plug(mainMenu)
        
    def initToolbar(self):
        toolbar = self.toolBar()
        self.newTraitAction.plug(toolbar)
        self.quitAction.plug(toolbar)
        
    def initlistView(self):
        self.listView.setRootIsDecorated(True)
        self.listView.addColumn('group')
        
    def refreshListView(self):
        self.listView.clear()
        trait_folder = KListViewItem(self.listView, 'traits')
        for trait in self.trait.get_trait_list():
            item = KListViewItem(trait_folder, trait)
            item.trait = trait

    def newTrait(self):
        dialog = SimpleRecordDialog(self, ['trait'])
        dialog.connect(dialog, SIGNAL('okClicked()'), self.insertNewTrait)
        self._dialog = dialog

    def insertNewTrait(self):
        dialog = self._dialog
        data = dialog.getRecordData()
        trait = data['trait']
        self.trait.create_trait(trait)
        self.refreshListView()
        
    def selectionChanged(self):
        current = self.listView.currentItem()
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
