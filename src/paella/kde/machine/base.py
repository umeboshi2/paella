from qt import SIGNAL
from qt import QLabel

from kdeui import KComboBox
from kdeui import KTextEdit
from kdeui import KLineEdit
from kdeui import KMessageBox

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


class BaseMachineDialog(VboxDialog):
    def __init__(self, parent, handler):
        VboxDialog.__init__(self, parent, 'BaseMachineDialog')
        self.handler = handler
        self._lists = dict(mtypes=[], profiles=[], kernels=[],
                           filesystems=[])
        self.dbaction = None
        self.connect(self, SIGNAL('okClicked()'), self.slotOkClicked)
        
    def _make_common_boxes(self):
        mtypes = self.handler.list_all_machine_types()
        self.mtypeLbl, self.mtypeBox = self._make_box('Machine Type', mtypes)
        profiles = self.handler.list_all_profiles()
        self.profileLbl, self.profileBox = self._make_box('Profile', profiles)
        kernels = self.handler.list_all_kernels()
        self.kernelLbl, self.kernelBox = self._make_box('Kernel', kernels)
        filesystems = self.handler.list_all_filesystems()
        self.fsLbl, self.fsBox = self._make_box('Filesystem', filesystems)
        self._lists = dict(mtypes=mtypes, profiles=profiles,
                           kernels=kernels, filesystems=filesystems)

    def _make_box(self, text, choices):
        lbl = QLabel(self.frame)
        lbl.setText(text)
        box = KComboBox(self.frame)
        box.insertStrList(choices)
        self.vbox.addWidget(lbl)
        self.vbox.addWidget(box)
        return lbl, box

    def _get_common_data(self):
        machine_type = str(self.mtypeBox.currentText())
        profile = str(self.profileBox.currentText())
        kernel = str(self.kernelBox.currentText())
        filesystem = str(self.fsBox.currentText())
        return machine_type, profile, kernel, filesystem

    def _get_common_data_dict(self):
        values = self._get_common_data()
        keys = ['machine_type', 'profile', 'kernel', 'filesystem']
        return dict(zip(keys, values))
    
    
    def slotOkClicked(self):
        mtype, profile, kernel, filesystem = self._get_common_data()
        if self.dbaction == 'insert':
            machine = str(self.machnameEntry.text())
            self.handler.make_a_machine(machine, mtype, profile,
                                        kernel, filesystem)
            performed = 'inserted'
        elif self.dbaction == 'update':
            machine = self.machine
            self.handler.update_a_machine(machine, mtype, profile,
                                          kernel, filesystem)
            performed = 'updated'
        else:
            raise RuntimeError, 'bad dbaction %s' % self.dbaction
        KMessageBox.information(self, '%s %s' % (machine, performed))

class NewMachineDialog(BaseMachineDialog):
    def __init__(self, parent, handler):
        BaseMachineDialog.__init__(self, parent, handler)
        self.machnameLbl = QLabel(self.frame)
        self.machnameLbl.setText('Machine Name')
        self.machnameEntry = KLineEdit(self.frame)
        self.vbox.addWidget(self.machnameLbl)
        self.vbox.addWidget(self.machnameEntry)
        self._make_common_boxes()
        self.dbaction = 'insert'
        

        
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
        mtype = self._lists['mtypes'].index(row.machine_type)
        self.mtypeBox.setCurrentItem(mtype)
        profile = self._lists['profiles'].index(row.profile)
        self.profileBox.setCurrentItem(profile)
        kernel = self._lists['kernels'].index(row.kernel)
        self.kernelBox.setCurrentItem(kernel)
        filesystem = self._lists['filesystems'].index(row.filesystem)
        self.fsBox.setCurrentItem(filesystem)
        
    
