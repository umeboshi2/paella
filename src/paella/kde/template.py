from qt import SLOT, SIGNAL, Qt
from qt import QSyntaxHighlighter
from qt import QColor, QWidget
from qt import QSplitter

from kdeui import KMainWindow
from kdeui import KPopupMenu
from kdeui import KMessageBox, KTextEdit
from kdeui import KListView, KListViewItem
from kdeui import KStdAction
#from kfile import KFileDialog

from paella.base.template import Template
from paella.profile.trait import Trait

from paella.kde.base.actions import ChangeSuiteAction
from paella.kde.db.gui import dbwidget, SuiteSelector
from paella.kde.differ import TraitList


class TemplateHighlighter(QSyntaxHighlighter):
    def highlightParagraph(self, text, endStateOfLastPara):
        text = str(text)
        template = Template()
        template.set_template(text)
        for span in template.spans():
            font = self.textEdit().currentFont()
            font.setBold(True)
            color =QColor('purple')
            length = span[1] - span[0]
            self.setFormat(span[0], length, font, color)
        return 0

class SimpleEdit(KTextEdit):
    def __init__(self, app, parent):
        KTextEdit.__init__(self, parent)
        self.app = app
        self.hl = TemplateHighlighter(self)
        
class TemplateEditor(QSplitter):
    def __init__(self, app, parent, suite, name='TemplateEditor'):
        QSplitter.__init__(self, parent, name)
        dbwidget(self, app)
        self.trait = None
        self.listView = TraitList(self.app, self, 'template')
        self.mainEdit = SimpleEdit(self.app, self)
        self.set_suite(suite)
        self.refreshListView()
        self.connect(self.listView,
                     SIGNAL('selectionChanged()'), self.selectionChanged)
          
    def set_suite(self, suite):
        self.suite = suite
        self.listView.set_suite(suite)
        self.trait = Trait(self.conn, suite=suite)
        
    def set_trait(self, trait):
        self.trait.set_trait(trait)

    def refreshListView(self):
        self.listView.refreshlistView()

    def selectionChanged(self):
        current = self.listView.currentItem()
        if hasattr(current, 'row'):
            self.mainEdit.setText(self.listView.getData())
            
class TemplateEditorWindow(KMainWindow):
    def __init__(self, app, parent, suite):
        KMainWindow.__init__(self, parent)
        dbwidget(self, app)
        self.mainView = TemplateEditor(self.app, self, suite)
        self.setCentralWidget(self.mainView)
        self.initActions()
        self.initMenus()
        self.initToolbar()
        self.show()
        
        
    def initActions(self):
        collection = self.actionCollection()
        self.changeSuiteAction = ChangeSuiteAction(self.slotChangeSuite, collection)
        self.quitAction = KStdAction.quit(self.close, collection)
        
    def initMenus(self):
        mainMenu = KPopupMenu(self)
        self.menuBar().insertItem('&Main', mainMenu)
        self.menuBar().insertItem('&Help', self.helpMenu(''))
        actions = [self.changeSuiteAction,
                   self.quitAction]
        for action in actions:
            action.plug(mainMenu)
        
    def initToolbar(self):
        toolbar = self.toolBar()
        actions = [self.changeSuiteAction,
                   self.quitAction]
        for action in actions:
            action.plug(toolbar)

    def initlistView(self):
        self.listView.setRootIsDecorated(True)
        self.listView.addColumn('group')
        
    def refreshListView(self):
        trait_folder = KListViewItem(self.listView, 'traits')
        for trait in self.trait.get_trait_list():
            item = KListViewItem(trait_folder, trait)
            item.trait = trait
            for widget in ['trait', 'template', 'environ', 'scripts']:
                w = KListViewItem(item, widget)
                w.trait = item.trait
                w.widget = widget
                
    def selectionChanged(self):
        current = self.listView.currentItem()
        if hasattr(current, 'trait'):
            print 'trait is', current.trait
            self.view.set_trait(current.trait)
        if hasattr(current, 'suite'):
            print 'suite is', current.suite
            if hasattr(current, 'widget'):
                print 'widget is', current.widget

    def slotChangeSuite(self):
        print 'ChangeSuite'
        win = SuiteSelector(self.app, self)
        win.connect(win, SIGNAL('okClicked()'), self.set_suite)
        self._suitedialog = win
        
    def set_suite(self):
        item = self._suitedialog.listView.currentItem()
        self.mainView.set_suite(item.suite)
        self.mainView.refreshListView()
        
        
        
if __name__ == '__main__':
    cfg = PaellaConfig()
    conn = PaellaConnection(cfg)
    t = Trait(conn, suite='kudzu')
