from qt import SIGNAL

from kdeui import KStdAction
from kdeui import KPopupMenu
from kdeui import KListViewItem

from useless.kdebase.mainwin import BaseSplitWindow
from useless.kdebase.dialogs import BaseRecordDialog

from paella.db.trait import Trait

from paella.kdenew.base.mainwin import BasePaellaWindow

from viewbrowser import TraitView


# quick hacky class to remind me of unimplemented classes
class _unimp(object):
    def __init__(self):
        self._nonimplemented(self.__class__.__name__)
    def _nonimplemented(self, objname):
        raise NotImplementedError, '%s is not implemented yet.' % objname
###########
    
class PackageView(_unimp):
    pass

class PackageSelector(_unimp):
    pass

class PackageSelectorWindow(_unimp):
    pass
###############


class NewTraitDialog(BaseRecordDialog):
    def __init__(self, parent, name='NewTraitDialog'):
        BaseRecordDialog.__init__(self, parent, ['name'], name=name)
        self.setCaption('Add a new trait')
        

# main window to handle traits
class TraitMainWindow(BaseSplitWindow, BasePaellaWindow):
    def __init__(self, parent, suite):
        BaseSplitWindow.__init__(self, parent, TraitView,
                                 name='TraitMainWindow-%s' % suite)
        # from BasePaellaWindow
        self.initPaellaCommon()
        self.initActions()
        self.initMenus()
        self.initToolbar()
        self.mainView.set_suite(suite)
        self.setCaption('%s traits' % suite)
        # these values should be in a configfile
        self.resize(500, 800)
        self.splitter.setSizes([100, 400])
        self.trait = Trait(self.conn, suite=suite)
        self.refreshListView()
    
    
        
    def initActions(self):
        collection = self.actionCollection()
        self.quitAction = KStdAction.quit(self.close, collection)
        self.newTraitAction = KStdAction.openNew(self.newTrait, collection)

    def initMenus(self):
        mainmenu = KPopupMenu(self)
        menus = [mainmenu]
        menubar = self.menuBar()
        menubar.insertItem('&Main', mainmenu)
        menubar.insertItem('&Help', self.helpMenu(''))
        self.newTraitAction.plug(mainmenu)
        self.quitAction.plug(mainmenu)

    def initToolbar(self):
        toolbar = self.toolBar()
        self.newTraitAction.plug(toolbar)
        self.quitAction.plug(toolbar)

    def initlistView(self):
        self.listView.addColumn('trait')

    def refreshListView(self):
        self.listView.clear()
        for trait in self.trait.get_trait_list():
            item = KListViewItem(self.listView, trait)
            item.trait = trait

    def newTrait(self):
        win = NewTraitDialog(self)
        win.frame.text_label.setText('Add a new trait.')
        win.connect(win, SIGNAL('okClicked()'), self.insertNewTrait)
        win.show()
        self._new_trait_dialog = win
        
    def insertNewTrait(self):
        dialog = self._new_trait_dialog
        trait = dialog.getRecordData()['name']
        self.trait.create_trait(trait)
        self.refreshListView()
        

    def selectionChanged(self):
        item = self.listView.currentItem()
        self.mainView.set_trait(item.trait)
        

if __name__ == '__main__':
        p = PackageView()
