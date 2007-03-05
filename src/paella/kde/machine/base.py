from kdeui import KComboBox
from kdeui import KTextEdit

from useless.kdebase.dialogs import VboxDialog

from paella.db.schema.tables import MTSCRIPTS

class MTScriptComboBox(KComboBox):
    def __init__(self, parent):
        KComboBox.__init__(self, parent, 'MTScriptComboBox')
        self.insertStrList(MTSCRIPTS)

class NewMTScriptDialog(VboxDialog):
    def __init__(self, parent):
        VboxDialog.__init__(self, parent, 'NewMTScriptDialog')
        self.scriptnameBox = MTScriptComboBox(self.frame)
        self.scriptdataBox = KTextEdit(self.frame)
        self.vbox.addWidget(self.scriptnameBox)
        self.vbox.addWidget(self.scriptdataBox)

    def getRecordData(self):
        name = str(self.scriptnameBox.currentText())
        data = str(self.scriptdataBox.text())
        return dict(name=name, data=data)

class NewMachineDialog(VboxDialog):
    def __init__(self, parent, handler):
        VboxDialog.__init__(self, parent, 'NewMachineDialog')
        self.handler = handler
        self.conn = self.handler.conn
        self.mtypeBox = KComboBox(self.frame)
        self.mtypeBox.insertStrList(self.handler.list_all_machine_types())
        self.profileBox = KComboBox(self.frame)
        self.profileBox.insertStrList(self.handler.list_all_profiles())
        self.kernelBox = KComboBox(self.frame)
        self.kernelBox.insertStrList(self.handler.list_all_kernels())
        self.fsBox = KComboBox(self.frame)
        self.fsBox.insertStrList(self.handler.list_all_filesystems())
        boxes = [self.mtypeBox, self.profileBox, self.kernelBox,
                 self.fsBox]
        for box in boxes:
            self.vbox.addWidget(box)
            
        
