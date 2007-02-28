from kdeui import KDialogBase
from kdeui import KComboBox

from useless.kdebase.dialogs import BaseRecordDialog

from paella.db.base import SuiteCursor

from widgets import BasePaellaWidget

        
        
class SuiteComboBox(KComboBox, BasePaellaWidget):
    def __init__(self, parent, name='SuiteComboBox'):
        KComboBox.__init__(self, parent, name)
        self.initPaellaCommon()
        self.suites = SuiteCursor(self.conn)
        self.insertStrList(self.suites.get_suites())


class SuiteSelectDialog(KDialogBase, BasePaellaWidget):
    def __init__(self, parent, name='SuiteSelectDialog'):
        KDialogBase.__init__(self, parent, name)
        self.suite = SuiteComboBox(self)
        self.setMainWidget(self.suite)

class NewTraitVariableDialog(BaseRecordDialog):
    def __init__(self, parent, name='NewTraitVariableDialog'):
        BaseRecordDialog.__init__(self, parent, ['name', 'value'], name=name)
        self.frame.text_label.setText('Make a new trait variable.')
        

        
