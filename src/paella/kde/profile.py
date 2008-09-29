from qt import SIGNAL
from qt import PYSIGNAL
from qt import QListBoxText

from kdeui import KMessageBox
from kdeui import KStdAction
from kdeui import KPopupMenu
from kdeui import KListViewItem

from paella.db.profile import Profile
from paella.db.family import Family

from useless.kdebase import get_application_pointer
from useless.kdebase.dialogs import BaseAssigner
from useless.kdebase.dialogs import BaseRecordDialog
from useless.kdebase.mainwin import BaseSplitWindow

from paella.kde.base import split_url
from paella.kde.base.viewbrowser import ViewBrowser
from paella.kde.base.mainwin import BasePaellaWindow
from paella.kde.base.dialogs import SuiteSelectDialog
from paella.kde.docgen.profile import ProfileDoc

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
        action, context, ident = split_url(url)
        if action == 'show':
            print 'unimpletmented'
        elif action == 'edit':
            if context == 'traits':
                win = TraitAssigner(self.parent(), ident)
                self.connect(win, SIGNAL('okClicked()'), self.resetView)
                win.show()
            elif context == 'variables':
                self.doc.profile.edit_variables()
                self.resetView()
            elif context == 'families':
                win = FamilyAssigner(self.parent(), ident)
                self.connect(win, SIGNAL('okClicked()'), self.resetView)
                win.show()
            else:
                KMessageBox.error(self, 'bad edit action %s' % url)
        elif action == 'change':
            if context == 'suite':
                self.emit(PYSIGNAL('changeSuite'), (ident,))
                print 'changeSuite emitted'
            else:
                KMessageBox.error(self, 'bad change action %s' % url)
        elif action == 'delete':
            if context == 'profile':
                msg = "Really delete profile %s" % ident
                answer = KMessageBox.questionYesNo(self, msg)
                if answer == KMessageBox.Yes:
                    #msg = "we're supposed to delete this profile, but can't yet"
                    self.doc.profile.delete_profile(ident)
                    msg = "profile %s deleted" % ident
                    KMessageBox.information(self, msg)
                    mainwin = self.parent().parent()
                    mainwin.refreshListView()
                    mainwin.resetProfileObject()
                    self.setText('')
                    
            else:
                KMessageBox.error(self, "Don't know how to delete %s" % context)
                
                
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
        self.splitter.setSizes([150, 450])
        self.setCaption('Paella Profiles')
        self._dialog = None
        self.connect(self.mainView, PYSIGNAL('changeSuite'), self.slotChangeSuite)
        
    def initActions(self):
        collection = self.actionCollection()
        self.quitAction = KStdAction.quit(self.close, collection)
        self.newProfileAction = KStdAction.openNew(self.newProfile, collection)
        self.importProfileAction = KStdAction.open(self.slotImportProfile, collection)
        self.exportProfileAction = KStdAction.saveAs(self.slotExportProfile, collection)
        
    def initMenus(self):
        mainmenu = KPopupMenu(self)
        menubar = self.menuBar()
        menubar.insertItem('&Main', mainmenu)
        menubar.insertItem('&Help', self.helpMenu(''))
        self.newProfileAction.plug(mainmenu)
        self.importProfileAction.plug(mainmenu)
        self.exportProfileAction.plug(mainmenu)
        self.quitAction.plug(mainmenu)

    def initToolbar(self):
        toolbar = self.toolBar()
        self.newProfileAction.plug(toolbar)
        self.importProfileAction.plug(toolbar)
        self.exportProfileAction.plug(toolbar)
        self.quitAction.plug(toolbar)

    def initlistView(self):
        self.listView.setRootIsDecorated(False)
        self.listView.addColumn('profile')
        self.listView.addColumn('suite')
        
    def refreshListView(self):
        self.listView.clear()
        for row in self.profile.select(fields=['profile', 'suite'], order=['profile']):
            item = KListViewItem(self.listView, row.profile, row.suite)
            item.profile = row.profile

    def newProfile(self):
        win = BaseRecordDialog(self, ['name'])
        win.frame.text_label.setText('Name for new profile:')
        win.connect(win, SIGNAL('okClicked()'), self.insertNewProfile)
        skeleton = self.cfg.get('management_gui', 'template_profile')
        if skeleton not in self.profile.get_profile_list():
            msg = 'Name for new profile: (skeleton does not exist yet.)'
            win.frame.text_label.setText(msg)
            win.setRecordData(dict(name=skeleton))
        win.show()
        self._dialog = win

    def insertNewProfile(self):
        win = self._dialog
        profile = win.getRecordData()['name']
        profile_list = self.profile.get_profile_list()
        if profile not in profile_list:
            skeleton = self.cfg.get('management_gui', 'template_profile')
            if skeleton in profile_list:
                self.profile.copy_profile(skeleton, profile)
                self.refreshListView()
            else:
                dlg = BaseRecordDialog(win, ['suite'])
                dlg.frame.text_label.setText('Select a suite for this profile')
                dlg.connect(dlg, SIGNAL('okClicked()'), self.insertNewProfilewithSuite)
                dlg.show()
                dlg.profile = profile
                win.suite_dialog = dlg
                KMessageBox.information(self, 'need to select suite here')
                
            # need to determine if skeleton exists
            KMessageBox.information(self, 'make profile %s' % profile)
        else:
            KMessageBox.error(self, 'Profile %s already exists.' % profile)

    def insertNewProfilewithSuite(self):
        win = self._dialog.suite_dialog
        profile = win.profile
        suite = win.getRecordData()['suite']
        self.profile.make_new_profile(profile, suite)
        self._dialog = None
        self.refreshListView()
    
    def selectionChanged(self):
        item = self.listView.currentItem()
        self.mainView.set_profile(item.profile)
        self.profile.set_profile(item.profile)

    def slotChangeSuite(self):
        win = SuiteSelectDialog(self)
        win.connect(win, SIGNAL('okClicked()'), self.slotSuiteSelected)
        win.show()
        self._dialog = win
        
    def slotSuiteSelected(self):
        win = self._dialog
        suite = str(win.suite.currentText())
        KMessageBox.information(self, 'change to suite %s' % suite)
        if suite != self.profile.current.suite:
            self.profile.set_suite(suite)
            self.mainView.resetView()
            
    def slotImportProfile(self):
        KMessageBox.information(self, 'Import unimplemented')

    def slotExportProfile(self):
        KMessageBox.information(self, 'Export unimplemented')

    def resetProfileObject(self):
        self.profile = Profile(self.conn)
        
        
