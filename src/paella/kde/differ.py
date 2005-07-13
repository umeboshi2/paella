from qt import SIGNAL, SLOT, Qt
from qt import QWidget
from qt import QVBoxLayout, QHBoxLayout

from kdeui import KMainWindow, KPushButton
from kdeui import KListView, KListViewItem
from kdeui import KStdAction, KPopupMenu
from kdeui import KComboBox

from useless.kbase.gui import MyCombo

from paella.sqlgen.clause import Eq

from paella.profile.base import Differ, Suites, Traits
from paella.profile.trait import TraitTemplate, TraitScript
from paella.profile.family import Family, FamilyVariablesConfig

from paella.kde.base.actions import DiffAction
from paella.kde.db.gui import dbwidget
    
class SuiteCombo(MyCombo):
    def __init__(self, parent, suites, name='SuiteCombo'):
        MyCombo.__init__(self, parent, name)
        self.fill(suites)

class TraitList(KListView):
    def __init__(self, app, parent, ftype='template', name='TraitList'):
        KListView.__init__(self, parent, name)
        dbwidget(self, app)
        self.ftype = ftype
        self.scripts = None
        self.templates = None
        self.traits = None
        self.trait = None
        self.setRootIsDecorated(True)
        self.addColumn('trait/file')
        self.addColumn('name')
        self.addColumn('package')
        
    def set_suite(self, suite):
        self.scripts = TraitScript(self.conn, suite)
        self.templates = TraitTemplate(self.conn, suite)
        self.traits = Traits(self.conn, suite)
        

    def set_trait(self, trait):
        self.trait = trait
        
    def refreshlistView(self):
        self.clear()
        if self.ftype == 'template':
            self.setColumnText(1, 'template')
        elif self.ftype == 'script':
            self.setColumnText(1, 'script')
        if self.trait is None:
            traits = self.traits.list()
        else:
            traits = [self.trait]
        for trait in traits:
            item = KListViewItem(self, trait)
            item.trait = trait
            if self.ftype == 'template':
                for row in self.templates.templates(trait):
                    titem = KListViewItem(item, str(row.templatefile), row.template, row.package)
                    titem.trait = trait
                    titem.row = row
            elif self.ftype == 'script':
                for row in self.scripts.cmd.select(clause=Eq('trait', trait), order='script'):
                    sitem = KListViewItem(item, str(row.scriptfile), row.script)
                    sitem.trait = trait
                    sitem.row = row
                    
    def getData(self):
        item = self.currentItem()
        if self.ftype == 'template':
            self.templates.set_trait(item.trait)
            return self.templates.templatedata(item.row.package, item.row.template)
        elif self.ftype == 'script':
            self.scripts.set_trait(item.trait)
            return self.scripts.scriptdata(item.row.script)

    def updateData(self, data):
        item = self.currentItem()
        row = item.row
        if self.ftype == 'template':
            self.templates.set_trait(item.trait)
            self.templates.update_templatedata(row.package, row.template, data)
        elif self.ftype == 'script':
            self.scripts.set_trait(item.trait)
            self.scripts.update_scriptdata(row.script, data)

class FamilyList(KListView):
    def __init__(self, app, parent, name='FamilyList'):
        KListView.__init__(self, parent, name)
        dbwidget(self, app)
        self.family = Family(self.conn)
        
        self.setRootIsDecorated(True)
        self.addColumn('family')
        self.refreshlistView()
        
    def refreshlistView(self):
        self.clear()
        rows = self.family.family_rows()
        for row in rows:
            item = KListViewItem(self, row.family)
            item.family = row.family

    def getData(self):
        item = self.currentItem()
        return FamilyVariablesConfig(self.conn, item.family)
    
    def updateData(self, data):
        pass
    
class SuiteTraitCombo(QWidget):
    def __init__(self, app, parent, name='SuiteTraitCombo'):
        QWidget.__init__(self, parent, name)
        dbwidget(self, app)
        self.suiteCursor = Suites(self.conn)
        self.suites = self.suiteCursor.list()
        self.traits = Traits(self.conn, self.suites[0])
        self.scombo = SuiteCombo(self, self.suites)
        self.tcombo = MyCombo(self, 'TypeCombo')
        self.tcombo.fill(['template', 'script'])
        self.trcombo = MyCombo(self, 'TraitCombo')
        self.ubutton = KPushButton('update', self)
        self.listView = TraitList(self.app, self)
        self.vbox = QVBoxLayout(self)
        for member in ['listView', 'scombo', 'tcombo', 'trcombo', 'ubutton']:
            widget = getattr(self, member)
            self.vbox.addWidget(widget)
        self.connect(self.scombo,
                     SIGNAL('highlighted(int)'), self.update_traits)
        self.connect(self.ubutton,
                     SIGNAL('clicked()'), self.refreshlistView)
        

    def update_traits(self):
        suite = str(self.scombo.currentText())
        self.traits.set_suite(suite)
        self.listView.set_suite(suite)
        self.listView.ftype = str(self.tcombo.currentText())
        
    def refreshlistView(self):
        trait = str(self.trcombo.currentText())
        if trait:
            self.listView.set_trait(trait)
        self.listView.ftype = str(self.tcombo.currentText())
        suite = str(self.scombo.currentText())
        self.listView.set_suite(suite)
        self.traits.set_suite(suite)
        traits = [row.trait for row in self.traits.select()]
        self.trcombo.fill(traits)
        if trait in traits:
            self.trcombo.setCurrentItem(traits.index(trait))
        self.listView.refreshlistView()

    def getData(self):
        return self.listView.getData()

    def updateData(self, data):
        self.listView.updateData(data)
    
class BaseDifferWidget(QWidget):
    def __init__(self, app, parent, dtype='trait', name='BaseDiffer'):
        QWidget.__init__(self, parent, name)
        dbwidget(self, app)
        self.dtype = dtype
        if dtype == 'trait':
            boxtype = SuiteTraitCombo
        elif dtype == 'family':
            boxtype = FamilyList
        self.leftBox = boxtype(self.app, self, 'leftBox')
        self.rightBox = boxtype(self.app, self, 'rightBox')
        self.vbox = QVBoxLayout(self)
        self.list_hbox = QHBoxLayout(self.vbox, 5)
        self.list_hbox.addWidget(self.leftBox)
        self.list_hbox.addWidget(self.rightBox)
        
    def slotDiff(self):
        print 'diff me'
        #left_item = self.leftBox.currentItem()
        #right_item = self.rightBox.currentItem()
        ldata = self.leftBox.getData()
        rdata = self.rightBox.getData()
        if self.dtype == 'trait':
            differ = Differ(ldata, rdata)
            differ.diff()
            if differ.isdifferent('left', ldata):
                newdata = differ.get_data('left')
                self.leftBox.updateData(newdata)
            if differ.isdifferent('right', rdata):
                newdata = differ.get_data('right')
                self.rightBox.updateData(newdata)
        elif self.dtype == 'family':
            ldata.diff(rdata)
            
        
    
class DifferWin(KMainWindow):
    def __init__(self, app, parent, dtype):
        KMainWindow.__init__(self, parent)
        #self.app = app
        dbwidget(self, app)
        
        self.mainView = BaseDifferWidget(self.app, self, dtype)
        self.initActions()
        self.initMenus()
        self.initToolbar()

        self.setCentralWidget(self.mainView)
        self.show()
        

    def initActions(self):
        collection = self.actionCollection()
        self.diffAction = DiffAction(self.mainView.slotDiff, collection)
        self.quitAction = KStdAction.quit(self.close, collection)
       
    def initMenus(self):
        mainMenu = KPopupMenu(self)
        menus = [mainMenu]
        self.menuBar().insertItem('&Main', mainMenu)
        self.menuBar().insertItem('&Help', self.helpMenu(''))
        for menu in menus:
            self.diffAction.plug(menu)
            self.quitAction.plug(menu)
            
    def initToolbar(self):
        print 'initToolbar'
        toolbar = self.toolBar()
        actions = [self.diffAction, self.quitAction]
        for action in actions:
            action.plug(toolbar)
            
