from qt import PYSIGNAL

from kdeui import KDialogBase
from kdeui import KComboBox

from useless.kdebase import get_application_pointer
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
        

class PaellaConnectionDialog(BaseRecordDialog):
    def __init__(self, parent, name='PaellaConnectionDialog'):
        fields = ['dbhost', 'dbname', 'dbusername', 'dbpassword']
        BaseRecordDialog.__init__(self, parent, fields, name=name)
        self.frame.text_label.setText('Connect to a database.')
        self.setButtonOKText('connect', 'connect')
        self.app = get_application_pointer()

    def slotConnectDatabase(self):
        data = self.getRecordData()
        data['autocommit'] = 'true'
        self.app.connect_database(data)
        self.emit(PYSIGNAL('dbconnected(data)'), (data,))
        
