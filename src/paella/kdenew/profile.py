from qt import SIGNAL
from qt import QListBoxText

from kdeui import KMessageBox
from kdeui import KStdAction
from kdeui import KPopupMenu
from kdeui import KListViewItem

from paella.db.profile import Profile
from paella.db.family import Family

from useless.kdebase import get_application_pointer
from useless.kdebase.dialogs import BaseAssigner
from useless.kdebase.mainwin import BaseSplitWindow

from paella.kdenew.base import split_url
from paella.kdenew.base.viewbrowser import ViewBrowser
from paella.kdenew.base.mainwin import BasePaellaWindow
from paella.kdenew.docgen.profile import ProfileDoc

class TraitAssigner(BaseAssigner):
    def __init__(self, parent, profile):
        self.app = get_application_pointer()
        self.conn = self.app.conn
        self.profile = Profile(self.conn)
        self.profile.set_profile(profile)
        BaseAssigner.__init__(self, parent, name='TraitAssigner',
                              udbuttons=True)
        self.connect(self, SIGNAL('okClicked()'), self.slotInsertNewTraits)

    def initView(self):
        self.suite = self.profile.current.suite
        # self.traits is just a cursor
        self.traits = self.conn.cursor(statement=True)
        self.traits.set_table('%s_traits' % self.suite)

        ptrows = self.profile.get_trait_rows()
        pt = [row.trait for row in ptrows]
        all_trows = self.traits.select(fields=['trait'], order=['trait'])
        trows = [row for row in all_trows if row.trait not in pt]
        abox = self.listBox.availableListBox()
        sbox = self.listBox.selectedListBox()
        for row in ptrows:
            r = QListBoxText(sbox, row.trait)
        for row in trows:
            r = QListBoxText(abox, row.trait)

    def slotInsertNewTraits(self):
        sbox = self.listBox.selectedListBox()
        traits = [str(sbox.item(n).text()) for n in range(sbox.numRows())]
        self.profile.insert_new_traits(traits)

class FamilyAssigner(BaseAssigner):
    def __init__(self, parent, profile):
        self.app = get_application_pointer()
        self.conn = self.app.conn
        self.profile = Profile(self.conn)
        self.profile.set_profile(profile)
        BaseAssigner.__init__(self, parent, name='FamilyAssigner',
                              udbuttons=True)
        self.connect(self, SIGNAL('okClicked()'), self.slotInsertNewFamilies)

    def initView(self):
        self.suite = self.profile.current.suite
        self.family = Family(self.conn)
        all_fams = self.family.all_families()
        pfams = self.profile.get_families()
        fams = [f for f in all_fams if f not in pfams]
        abox = self.listBox.availableListBox()
        sbox = self.listBox.selectedListBox()
        for family in pfams:
            self._add_family_to_listbox(sbox, family)
        for family in fams:
            self._add_family_to_listbox(abox, family)
            

    def _add_family_to_listbox(self, box, family):
        r = QListBoxText(box, family)
        r.family = family

    def slotInsertNewFamilies(self):
        sbox = self.listBox.selectedListBox()
        families =[str(sbox.item(n).text()) for n in range(sbox.numRows())]
        self.profile.delete_all_families()
        for family in families:
            self.profile.append_family(family)
        
        
class ProfileView(ViewBrowser):
    def __init__(self, parent):
        ViewBrowser.__init__(self, parent, ProfileDoc)

    def set_profile(self, profile):
        self.doc.set_profile(profile)
        self.setText(self.doc.output())

    def resetView(self):
        self.set_profile(self.doc.profile.current.profile)
        
    def set_suite(self, suite):
        self.doc.suite = suite
        self.doc.trait = Trait(self.app.conn, suite=suite)

    def setSource(self, url):
        action, context, id = split_url(url)
        if action == 'show':
            print 'unimpletmented'
        elif action == 'edit':
            if context == 'traits':
                win = TraitAssigner(self.parent(), id)
                self.connect(win, SIGNAL('okClicked()'), self.resetView)
                win.show()
            elif context == 'variables':
                self.doc.profile.edit_variables()
                self.resetView()
            elif context == 'families':
                win = FamilyAssigner(self.parent(), id)
                self.connect(win, SIGNAL('okClicked()'), self.resetView)
                win.show()
            else:
                KMessageBox.error(self, 'bad edit action %s' % url)
                
        else:
            KMessageBox.information(self, 'called %s' % url)
        
        
class ProfileMainWindow(BaseSplitWindow, BasePaellaWindow):
    def __init__(self, parent):
        BaseSplitWindow.__init__(self, parent, ProfileView,
                                 name='ProfileMainWindow')
        self.initPaellaCommon()
        self.initActions()
        self.initMenus()
        self.initToolbar()
        self.cursor = self.conn.cursor(statement=True)
        self.profile = Profile(self.conn)
        self.refreshListView()
        self.resize(600, 800)
        self.setCaption('Paella Profiles')

    def initActions(self):
        collection = self.actionCollection()
        self.quitAction = KStdAction.quit(self.close, collection)
        self.newProfileAction = KStdAction.openNew(self.newProfile, collection)

    def initMenus(self):
        mainmenu = KPopupMenu(self)
        menubar = self.menuBar()
        menubar.insertItem('&Main', mainmenu)
        menubar.insertItem('&Help', self.helpMenu(''))
        self.newProfileAction.plug(mainmenu)
        self.quitAction.plug(mainmenu)

    def initToolbar(self):
        toolbar = self.toolBar()
        self.newProfileAction.plug(toolbar)
        self.quitAction.plug(toolbar)

    def initlistView(self):
        self.listView.setRootIsDecorated(False)
        self.listView.addColumn('profile')

    def refreshListView(self):
        self.listView.clear()
        for row in self.profile.select(fields=['profile', 'suite'], order=['profile']):
            item = KListViewItem(self.listView, row.profile)
            item.profile = row.profile

    def newProfile(self):
        raise NotImplementedError, 'need a dialog box in newProfile'

    def selectionChanged(self):
        item = self.listView.currentItem()
        self.mainView.set_profile(item.profile)
        
