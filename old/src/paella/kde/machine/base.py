from pyPgSQL.libpq import OperationalError
from qt import SIGNAL
from qt import QLabel

from kdeui import KComboBox
from kdeui import KTextEdit
from kdeui import KLineEdit
from kdeui import KMessageBox

from useless.kdebase.dialogs import VboxDialog

from paella.db.schema.tables import MACHINE_SCRIPTS
from paella.db.machine.base import NoSuchKernelError

# this is inconsistent from the way the
# the trait scripts are selected
# we should probably use the database
# here instead of the hardcoded MACHINE_SCRIPTS
# list.
class MachineScriptComboBox(KComboBox):
    def __init__(self, parent):
        KComboBox.__init__(self, parent, 'MachineScriptComboBox')
        self.insertStrList(MACHINE_SCRIPTS)

class NewMachineScriptDialog(VboxDialog):
    def __init__(self, parent):
        VboxDialog.__init__(self, parent, 'NewMachineScriptDialog')
        self.scriptnameBox = MachineScriptComboBox(self.frame)
        self.scriptdataBox = KTextEdit(self.frame)
        self.vbox.addWidget(self.scriptnameBox)
        self.vbox.addWidget(self.scriptdataBox)

    def getRecordData(self):
        name = str(self.scriptnameBox.currentText())
        data = str(self.scriptdataBox.text())
        return dict(name=name, data=data)


class BaseMachineDialog(VboxDialog):
    def __init__(self, parent, handler):
        VboxDialog.__init__(self, parent, 'BaseMachineDialog')
        self.handler = handler
        self.dbaction = None
        self.connect(self, SIGNAL('okClicked()'), self.slotOkClicked)
        
    def slotOkClicked(self):
        raise NotImplementedError , "slotOkClicked not implemented in BaseMachineDialog"
    
class NewMachineDialog(BaseMachineDialog):
    def __init__(self, parent, handler):
        BaseMachineDialog.__init__(self, parent, handler)
        self.machnameLbl = QLabel(self.frame)
        self.machnameLbl.setText('Machine Name')
        self.machnameEntry = KLineEdit(self.frame)
        self.vbox.addWidget(self.machnameLbl)
        self.vbox.addWidget(self.machnameEntry)
        self.dbaction = 'insert'

    def slotOkClicked(self):
        machine = str(self.machnameEntry.text())
        print "slotOkClicked", machine
        self.handler.make_a_machine(machine)

class NewKernelDialog(BaseMachineDialog):
    def __init__(self, parent, handler):
        BaseMachineDialog.__init__(self, parent, handler)
        self.kernelLbl = QLabel(self.frame)
        self.kernelLbl.setText('Name of kernel package')
        self.kernelEntry = KLineEdit(self.frame)
        self.vbox.addWidget(self.kernelLbl)
        self.vbox.addWidget(self.kernelEntry)
        self.dbaction = 'insert'

    def slotOkClicked(self):
        kernel = str(self.kernelEntry.text())
        self.handler.add_kernel(kernel)
        
class BaseMachineAttributeDialog(BaseMachineDialog):
    def __init__(self, parent, handler, attribute):
        BaseMachineDialog.__init__(self, parent, handler)
        self.attributeLbl = QLabel(self.frame)
        self.attributeLbl.setText(attribute)
        self.attributeEntry = KLineEdit(self.frame)
        self.vbox.addWidget(self.attributeLbl)
        self.vbox.addWidget(self.attributeEntry)
        self.attribute = attribute

    def slotOkClicked(self):
        value = str(self.attributeEntry.text())
        try:
            self.handler.set_attribute(self.attribute, value)
        except OperationalError, inst:
            if 'violates foreign key constraint' in inst.message:
                KMessageBox.error(self, '%s is not a valid %s' % (value, self.attribute))
            else:
                raise OperationalError(inst)
        except NoSuchKernelError, inst:
            KMessageBox.error("There's no such kernel: %s" % value)
        
class MachineParentDialog(BaseMachineDialog):
    def __init__(self, parent, handler):
        BaseMachineDialog.__init__(self, parent, handler)
        self.parentLbl = QLabel(self.frame)
        self.parentLbl.setText("parent")
        self.parentEntry = KLineEdit(self.frame)
        self.vbox.addWidget(self.parentLbl)
        self.vbox.addWidget(self.parentEntry)

    def slotOkClicked(self):
        pass
    
class NewDiskConfigDialog(VboxDialog):
    def __init__(self, parent, handler):
        VboxDialog.__init__(self, parent)
        self.diskconfig = handler
        self.diskconfigLbl = QLabel(self.frame)
        self.diskconfigLbl.setText('DiskConfig Name')
        self.diskconfigEntry = KLineEdit(self.frame)
        self.contentLbl = QLabel(self.frame)
        self.contentLbl.setText('DiskConfig Content')
        self.contentEntry = KTextEdit(self.frame)
        self.vbox.addWidget(self.diskconfigLbl)
        self.vbox.addWidget(self.diskconfigEntry)
        self.vbox.addWidget(self.contentLbl)
        self.vbox.addWidget(self.contentEntry)
        self.connect(self, SIGNAL('okClicked()'), self.slotOkClicked)

    def slotOkClicked(self):
        name = str(self.diskconfigEntry.text())
        content = str(self.contentEntry.text())
        self.diskconfig.set(name, dict(content=content))
        
        
        
class EditMachineDIalog(BaseMachineDialog):
    def __init__(self, parent, handler, machine):
        BaseMachineDialog.__init__(self, parent, handler)
        self.machine = machine
        self.machLbl = QLabel(self.frame)
        self.machLbl.setText('Edit Machine %s' % machine)
        self.vbox.addWidget(self.machLbl)
        self._make_common_boxes()
        self._set_combo_boxes(self.handler.current)
        self.dbaction = 'update'
        
    def _set_combo_boxes(self, row):
        kernel = self._lists['kernels'].index(row.kernel)
        self.kernelBox.setCurrentItem(kernel)
        profile = self._lists['profiles'].index(row.profile)
        self.profileBox.setCurrentItem(profile)
        
    
