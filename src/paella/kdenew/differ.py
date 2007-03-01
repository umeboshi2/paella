from qt import QFrame
from qt import QVBoxLayout
from qt import QHBoxLayout
from qt import SIGNAL

from kdeui import KComboBox
from kdeui import KListView, KListViewItem
from kdeui import KPushButton

# for mainwin class
from kdeui import KStdAction
from kdeui import KPopupMenu

from useless.kdebase import get_application_pointer
from useless.sqlgen.clause import Eq

from paella.base.objects import Differ

from paella.db.base import Suites, Traits
from paella.db.trait.relations import TraitTemplate, TraitScript
from paella.db.family import Family, FamilyVariablesConfig

# for mainwin class
from paella.kdenew.base.actions import DiffAction

from paella.kdenew.base.mainwin import BasePaellaWindow

from useless.kdebase.error import MethodNotImplementedError

class TraitListView(KListView):
    def __init__(self, parent, file_type='template', name='TraitListView'):
        KListView.__init__(self, parent, name)
        self.app = get_application_pointer()
        self.conn = self.app.conn
        self.file_type = file_type
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
        self.setColumnText(1, self.file_type)
        if self.trait is None:
            traits = self.traits.list()
        else:
            traits = [self.trait]
        for trait in traits:
            item = KListViewItem(self, trait)
            item.trait = trait
            # expand tree by default
            item.setOpen(True)
            if self.file_type == 'template':
                for row in self.templates.templates(trait):
                    template_item = KListViewItem(item, str(row.templatefile),
                                                  row.template)
                    template_item.trait = trait
                    template_item.row = row
            elif self.file_type == 'script':
                # perhaps we need to make a method to obtain scriptnames
                # in TraitScript object
                for row in self.scripts.cmd.select(clause=Eq('trait', trait), order='script'):
                    script_item = KListViewItem(item, str(row.scriptfile), row.script)
                    script_item.trait = trait
                    script_item.row = row
            else:
                raise ValueError, "unknown file_type %s" % self.file_type

    # get template or script contents
    def getData(self):
        item = self.currentItem()
        if self.file_type == 'template':
            self.templates.set_trait(item.trait)
            return self.templates.templatedata(item.row.template)
        elif self.file_type == 'script':
            self.scripts.set_trait(item.trait)
            return self.scripts.scriptdata(item.row.script)
        else:
            raise ValueError, "unknown file_type %s" % self.file_type

    # replace template or script contents
    def updateData(self, data):
        item = self.currentItem()
        row = item.row
        if self.file_type == 'template':
            self.templates.set_trait(item.trait)
            self.templates.update_templatedata(row.template, data)
        elif self.file_type == 'script':
            self.scripts.set_trait(item.trait)
            self.scripts.update_scriptdata(row.script, data)
        else:
            raise ValueError, "unknown file_type %s" % self.file_type

class FamilyList(KListView):
    def __init__(self, parent, name='FamilyList'):
        KListView.__init__(self, parent, name)
        self.app = get_application_pointer()
        self.conn = self.app.conn
        
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
        raise MethodNotImplementedError(self, 'FamilyList.updateData')
    
            
class SuiteTraitComboBox(QFrame):
    def __init__(self, parent, name='SuiteTraitComboBox'):
        QFrame.__init__(self, parent, name)
        self.app = get_application_pointer()
        self.conn = self.app.conn
        self.suiteCursor = Suites(self.conn)
        self.suites = self.suiteCursor.list()
        self.traits = Traits(self.conn, self.suites[0])
        self.scombo = KComboBox(self, 'SuiteComboBox')
        self.scombo.insertStrList(self.suites)
        self.tcombo = KComboBox(self, 'TypeComboBox')
        self.tcombo.insertStrList(['template', 'script'])
        self.trcombo = KComboBox(self, 'TraitComboBox')
        self.update_btn = KPushButton('update', self)
        self.listView = TraitListView(self)
        self.vbox = QVBoxLayout(self)
        for attribute in ['listView', 'scombo', 'tcombo', 'trcombo', 'update_btn']:
            widget = getattr(self, attribute)
            self.vbox.addWidget(widget)
        # we need to redo the signals and the methods that are called
        self.connect(self.scombo,
                     SIGNAL('activated(int)'), self.update_traits)
        
        self.connect(self.update_btn,
                     SIGNAL('clicked()'), self.refreshlistView)

    def update_traits(self, suite_index):
        suite = self.suites[suite_index]
        self.traits.set_suite(suite)
        self.listView.set_suite(suite)
        self.listView.file_type = str(self.tcombo.currentText())
        traits = [row.trait for row in self.traits.select()]
        traits.sort()
        self.trcombo.clear()
        self.trcombo.insertStrList(traits)
        

    def refreshlistView(self):
        trait = str(self.trcombo.currentText())
        if trait:
            self.listView.set_trait(trait)
        self.listView.file_type = str(self.tcombo.currentText())
        suite = str(self.scombo.currentText())
        self.traits.set_suite(suite)
        self.listView.set_suite(suite)
        traits = [row.trait for row in self.traits.select()]
        self.trcombo.clear()
        self.trcombo.insertStrList(traits)
        if trait in traits:
            self.trcombo.setCurrentItem(traits.index(trait))
        self.listView.refreshlistView()

    # returns template or script contents
    def getData(self):
        return self.listView.getData()

    # replace template or script contents
    def updateData(self, data):
        self.listView.updateData(data)

class BaseDifferFrame(QFrame):
    def __init__(self, parent, diff_type='trait', name='BaseDifferFrame'):
        QFrame.__init__(self, parent, name)
        self.diff_type = diff_type
        if self.diff_type == 'trait':
            boxtype = SuiteTraitComboBox
        elif self.diff_type == 'family':
            boxtype = FamilyList
        else:
            raise ValueError, 'unknown diff_type %s' % self.diff_type
        self.leftBox = boxtype(self, 'leftBox')
        self.rightBox = boxtype(self, 'rightBox')
        self.vbox = QVBoxLayout(self)
        margin = 5
        self.list_hbox = QHBoxLayout(self.vbox, margin)
        self.list_hbox.addWidget(self.leftBox)
        self.list_hbox.addWidget(self.rightBox)

    def slotDiff(self):
        left_data = self.leftBox.getData()
        right_data = self.rightBox.getData()
        if self.diff_type == 'trait':
            differ = Differ(left_data, right_data)
            differ.diff()
            if differ.isdifferent('left', left_data):
                newdata = differ.get_data('left')
                self.leftBox.updateData(newdata)
            if differ.isdifferent('right', right_data):
                newdata = differ.get_data('right')
                self.rightBox.updateData(newdata)
        elif self.diff_type == 'family':
            # VariablesConfig objects have their own diff method
            left_data.diff(right_data)
        else:
            raise ValueError, 'unknown diff_type %s' % self.diff_type

class DifferWindow(BasePaellaWindow):
    def __init__(self, parent, diff_type, name='DifferWindow'):
        BasePaellaWindow.__init__(self, parent, name=name)
        self.mainView = BaseDifferFrame(self, diff_type)
        self.initActions()
        self.initMenus()
        self.initToolbar()
        self.setCentralWidget(self.mainView)
        self.setCaption('%s Differ' % diff_type.capitalize())
        
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
            

            
