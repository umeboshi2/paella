from kdeui import KStdAction
from kdeui import KPopupMenu
from kdeui import KListViewItem

from useless.kdebase.error import MethodNotImplementedError
from useless.kdebase.mainwin import BaseSplitWindow

from paella.db.trait import Trait

from paella.kdenew.docgen.trait import TraitDoc
from paella.kdenew.base import split_url
from paella.kdenew.base.viewbrowser import ViewBrowser
from paella.kdenew.base.mainwin import BasePaellaWindow

# we need to cleanup the paella.kdenew.template module
from paella.kdenew.template import SimpleEdit

# quick hacky class to remind me of unimplemented classes
class _unimp(object):
    def __init__(self):
        self._nonimplemented(self.__class__.__name__)
    def _nonimplemented(self, objname):
        raise NotImplementedError, '%s is not implemented yet.' % objname
###########

class ViewWindow(BasePaellaWindow):
    def __init__(self, parent, view, name='ViewWindow'):
        BasePaellaWindow.__init__(self, parent, name)
        self.mainView = view(self)
        self.mainView.setReadOnly(True)
        self.setCentralWidget(self.mainView)
        self.resize(500, 600)
        
class PackageView(_unimp):
    pass

class PackageSelector(_unimp):
    pass

class PackageSelectorWindow(_unimp):
    pass

class TraitView(ViewBrowser):
    # The TraitDoc holds the main traitdb object
    def __init__(self, parent):
        ViewBrowser.__init__(self, parent, TraitDoc)
        # setup dialog pointers
        # just one now
        self._dialog = None
        
    def set_trait(self, trait):
        self.doc.set_trait(trait)
        self.setText(self.doc.output())

    def resetView(self):
        self.set_trait(self.doc.trait.current_trait)

    def set_suite(self, suite):
        self.doc.suite = suite
        self.doc.trait = Trait(self.app.conn, suite=suite)

    # handle url
    # this method is too long in original TraitView browser
    # this needs to split up into more methods
    def setSource(self, url):
        action, context, ident = split_url(url)
        if action == 'show':
            self._perform_show_action(context, ident)
        elif action == 'edit':
            self._perform_edit_action(context, ident)
        elif action == 'new':
            self._perform_new_action(context, ident)
        else:
            raise MethodNotImplementedError(self, url)

    # add package to trait from dialog
    def slotAddPackage(self):
        raise MethodNotImplementedError(self, 'TraitView.slotAddPackage')

    # tarball selected in dialog, make another dialog with url tar://filename
    def fileSelected(self):
        raise MethodNotImplementedError(self, 'TraitView.fileSelected')

    # template selected from tarball dialog
    def newTemplateSelected(self):
        raise MethodNotImplementedError(self, 'TraitView.newTemplateSelected')

    # don't know what job was supposed to be here
    def slotGetFromTarDone(self, job):
        raise MethodNotImplementedError(self, 'TraitView.slotGetFromTarDone')

    def _perform_show_action(self, context, ident):
        if context == 'parent':
            win = TraitMainWindow(self.parent(), self.doc.suite)
            win.mainView.set_trait(ident)
        elif context == 'template':
            print 'show template', ident
        elif context == 'script':
            # need to call public method here
            scriptfile = self.doc.trait._scripts.scriptdata(ident)
            win = ViewWindow(self.parent(), SimpleEdit, name='ScriptView')
            win.mainView.setText(scriptfile)
        else:
            raise MethodNotImplementedError(self, 'TraitView._perform_show_action')
        win.show()
    def _perform_edit_action(self, context, ident):
        raise MethodNotImplementedError(self, 'TraitView._perform_edit_action')
    def _perform_new_action(self, context, ident):
        raise MethodNotImplementedError(self, 'TraitView._perform_new_action')
    
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
        raise MethodNotImplementedError(self, 'TraitMainWindow.newTrait')

    def insertNewTrait(self):
        raise MethodNotImplementedError(self, 'TraitMainWindow.insertNewTrait')

    def selectionChanged(self):
        item = self.listView.currentItem()
        self.mainView.set_trait(item.trait)
        

if __name__ == '__main__':
        p = PackageView()
