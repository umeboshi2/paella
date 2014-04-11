from qt import SIGNAL
from qt import QListBoxText

from kdeui import KMessageBox
from kdeui import KStdAction
from kdeui import KPopupMenu
from kdeui import KListViewItem

from paella.db.family import Family

from useless.kdebase import get_application_pointer
from useless.kdebase.mainwin import BaseSplitWindow
from useless.kdebase.dialogs import BaseRecordDialog
from useless.kdebase.dialogs import BaseAssigner

from paella.kde.base import split_url
from paella.kde.base.viewbrowser import ViewBrowser
from paella.kde.base.mainwin import BasePaellaWindow
from paella.kde.docgen.family import FamilyDoc

class NewFamilyDialog(BaseRecordDialog):
    def __init__(self, parent, name='NewFamilyDialog'):
        BaseRecordDialog.__init__(self, parent, ['name'], name=name)
        self.setCaption('Add a new family')
        

class FamilyParentAssigner(BaseAssigner):
    def __init__(self, parent, family):
        self.app = get_application_pointer()
        self.conn = self.app.conn
        self.family = Family(self.conn)
        self.family.set_family(family)
        BaseAssigner.__init__(self, parent, name='FamilyParentAssigner',
                              udbuttons=False)
        self.connect(self, SIGNAL('okClicked()'), self.slotAssignParents)

    def initView(self):
        family = self.family.current
        all_fams = self.family.all_families()
        assigned_parents = self.family.parents()
        avail_parents = [f for f in all_fams if f not in assigned_parents + [family]]
        abox = self.listBox.availableListBox()
        sbox = self.listBox.selectedListBox()
        for family in assigned_parents:
            self._add_family_to_listbox(sbox, family)
        for family in avail_parents:
            self._add_family_to_listbox(abox, family)
        self.already_assigned = assigned_parents
        
    def _add_family_to_listbox(self, box, family):
        item = QListBoxText(box, family)
        item.family = family

    def slotAssignParents(self):
        sbox = self.listBox.selectedListBox()
        families =[str(sbox.item(n).text()) for n in range(sbox.numRows())]
        # since we're using a SimpleRelation class for
        # family.parents, we don't need to worry about
        # inserting families that are already there
        self.family.delete_parents()
        self.family.insert_parents(families)

        
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

    def resetView(self):
        self.set_family(self.family.current)
        

    def setSource(self, url):
        action, context, ident = split_url(url)
        if action == 'edit':
            if context == 'variables':
                config = self.family.getVariablesConfig(self.family.current)
                newconfig = config.edit()
                config.update(newconfig)
                self.set_family(ident)
            elif context == 'parents':
                dialog = FamilyParentAssigner(self, ident)
                dialog.connect(dialog, SIGNAL('okClicked()'), self.resetView)
                dialog.show()
            else:
                KMessageBox.error(self, 'unable to edit %s for family' % context)
        elif action == 'delete':
            if context == 'family':
                #KMessageBox.information(self, 'delete family %s is unimplemented' % ident)
                msg = "Really delete family %s" % ident
                answer = KMessageBox.questionYesNo(self, msg)
                if answer == KMessageBox.Yes:
                    self.family.delete_family(ident)
                    msg = "family %s deleted" % ident
                    KMessageBox.information(self, msg)
                    self.parent().parent().refreshListView()
                    self.setText('')
            else:
                KMessageBox.error(self, 'unable to delete %s for family' % context)
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
        self.splitter.setSizes([100, 500])
        self.setCaption('Paella Families')
        self._new_family_dialog = None

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
        win = NewFamilyDialog(self)
        win.frame.text_label.setText('Add a new family.')
        win.connect(win, SIGNAL('okClicked()'), self.insertNewFamily)
        win.show()
        self._new_family_dialog = win
        
    def insertNewFamily(self):
        win = self._new_family_dialog
        family = win.getRecordData()['name']
        self.family.create_family(family)
        self.refreshListView()
        self._new_family_dialog = None
        
        
    
    def slotImportFamily(self):
        KMessageBox.information(self, 'Import unimplemented')

    def slotExportFamily(self):
        KMessageBox.information(self, 'Export unimplemented')
        
        
