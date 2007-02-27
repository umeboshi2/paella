from qt import SIGNAL
from qt import QListBoxText

from kdeui import KComboBox
from kdeui import KDialogBase

from useless.db.midlevel import StatementCursor
from useless.kdebase import get_application_pointer
from useless.kdebase.dialogs import BaseAssigner

from paella.db.trait import Trait

from paella.kdenew.base.mainwin import BasePaellaWindow

class ViewWindow(BasePaellaWindow):
    def __init__(self, parent, view, name='ViewWindow'):
        BasePaellaWindow.__init__(self, parent, name)
        self.mainView = view(self)
        self.mainView.setReadOnly(True)
        self.setCentralWidget(self.mainView)
        self.resize(500, 600)
    

class ParentAssigner(BaseAssigner):
    def __init__(self, parent, trait, suite, name='ParentAssigner'):
        self.app = get_application_pointer()
        self.conn = self.app.conn
        self.suite = suite
        self.trait = Trait(self.conn, suite=self.suite)
        self.trait.set_trait(trait)
        BaseAssigner.__init__(self, parent, name=name)
        self.connect(self, SIGNAL('okClicked()'), self.slotInsertNewParents)
        
    def initView(self):
        traits = self.trait.get_trait_list()
        parents = self.trait.parents()
        traits = [t for t in traits if t != self.trait.current_trait]
        abox = self.listBox.availableListBox()
        sbox = self.listBox.selectedListBox()
        avail_traits = [t for t in traits if t not in parents]
        for trait in avail_traits:
            r = QListBoxText(abox, trait)
        for trait in parents:
            r = QListBoxText(sbox, trait)

    def slotInsertNewParents(self):
        sbox = self.listBox.selectedListBox()
        parents = [str(sbox.item(n).text()) for n in range(sbox.numRows())]
        self.trait.update_parents(parents)
        
class ScriptNameComboBox(KComboBox):
    def __init__(self, parent, name='ScriptNameComboBox'):
        KComboBox.__init__(self, parent, name)
        self.app = get_application_pointer()
        self.cursor = StatementCursor(self.app.conn)
        self.scriptnames = [row.script for row in  self.cursor.select(table='scriptnames')]
        self.insertStrList(self.scriptnames)

class ScriptNameDialog(KDialogBase):
    def __init__(self, parent, name='ScriptNameDialog'):
        KDialogBase.__init__(self, parent, name)
        self.scriptname_widget = ScriptNameComboBox(self)
        self.setMainWidget(self.scriptname_widget)

    def scriptname(self):
        return str(self.scriptname_widget.currentText())
    
