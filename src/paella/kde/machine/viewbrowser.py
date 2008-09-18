from qt import SIGNAL

from kdeui import KMessageBox

from useless.base.util import strfile
from useless.kdebase import get_application_pointer
from useless.kdebase.dialogs import BaseRecordDialog

from paella.kde.base import split_url
from paella.kde.base.viewbrowser import ViewBrowser

# import document objects
from paella.kde.docgen.machine import MachineDoc
from paella.kde.docgen.machine import MachineTypeDoc
from paella.kde.docgen.machine import DiskConfigDoc

from base import NewMachineDialog
from base import EditMachineDIalog
from base import NewMTScriptDialog
from base import NewDiskConfigDialog


class DiskConfigView(ViewBrowser):
    def __init__(self, parent):
        ViewBrowser.__init__(self, parent, DiskConfigDoc)

    def set_diskconfig(self, diskconfig):
        self.doc.set_diskconfig(diskconfig)
        self.setText(self.doc.output())

    def setSource(self, url):
        action, context, ident = split_url(url)
        if action == 'new':
            handler = self.doc.diskconfig
            dialog = NewDiskConfigDialog(self, handler)
            dialog.show()
            dialog.connect(dialog, SIGNAL('okClicked()'), self.parent().resetView)
            self._dialog = dialog
        elif action == 'edit':
            self.doc.diskconfig.edit_diskconfig(ident)
            self.parent().resetView()
        elif action == 'delete':
            self.doc.diskconfig.delete(ident)
            self.parent().resetView()
        else:
            msg = "unsupported action: %s" % action
            KMessageBox.error(self, msg)
    
            
class MachineView(ViewBrowser):
    def __init__(self, parent):
        ViewBrowser.__init__(self, parent, MachineDoc)

    def set_machine(self, machine):
        self.doc.set_machine(machine)
        self.setText(self.doc.output())

    def setSource(self, url):
        action, context, ident = split_url(url)
        if action == 'new':
            if context == 'machine':
                handler = self.doc.machine
                dialog = NewMachineDialog(self, handler)
                dialog.show()
                self._dialog = dialog
            else:
                KMessageBox.error(self, '%s not supported' % url)
        elif action == 'edit':
            if context == 'machine':
                handler = self.doc.machine
                dialog = EditMachineDIalog(self, handler, ident)
                dialog.show()
                self._dialog = dialog
                print 'edit machine', dialog.machine
        else:
            KMessageBox.error(self, '%s not supported' % url)

class MachineTypeView(ViewBrowser):
    def __init__(self, parent):
        ViewBrowser.__init__(self, parent, MachineTypeDoc)
        self._dialog = None

    def set_machine_type(self, machine_type):
        self.doc.set_machine_type(machine_type)
        self.setText(self.doc.output())

    def resetView(self):
        self.set_machine_type(self.doc.mtype.current)

    def setSource(self, url):
        action, context, ident = split_url(url)
        fields = []
        dialog_message = 'We need a message here'
        if context == 'Families':
            fields = ['family']
            dialog_message = 'Add a new family.'
        elif context == 'Variables':
            fields = ['name', 'value']
            dialog_message = 'Add a new variable.'
        elif context == 'machine_type':
            fields = ['name', 'parent', 'diskconfig']
            dialog_message = 'Add a new machine type.'
        if action == 'new':
            if context == 'Scripts':
                dialog = NewMTScriptDialog(self)
                dialog.connect(dialog, SIGNAL('okClicked()'), self.insertNewScript)
                self._dialog = dialog
            elif fields:
                dialog = BaseRecordDialog(self, fields)
                dialog.context = context
                dialog.connect(dialog, SIGNAL('okClicked()'), self.insertNewRecord)
                dialog.frame.setText(dialog_message)
                self._dialog = dialog
            else:
                KMessageBox.error(self, 'problem with %s' % url)
        elif action == 'edit':
            self._perform_edit_action(context, ident)
        elif action == 'delete':
            self._perform_delete_action(context, ident)
        else:
            msg = 'Problem with action in url %s' % url
            KMessageBox.error(self, msg)
        if self._dialog is not None:
            self._dialog.connect(self._dialog, SIGNAL('cancelClicked()'), self._destroy_dialog)
            self._dialog.show()
        if action != 'new':
            self.resetView()

    def _perform_delete_action(self, context, ident):
        if context == 'Families':
            self.doc.mtype.delete_family(ident)
            self.resetView()
        elif context == 'Variables':
            self.doc.mtype.edit_variables()
        elif context == 'Scripts':
            ans = KMessageBox.questionYesNo(self, "really delete this script?")
            if ans == KMessageBox.Yes:
                self.doc.mtype.delete_script(ident)
        elif context == 'Modules':
            msg = 'Deleting modules is not supported.'
            KMessageBox.information(self, msg)
        elif context == 'machine_type':
            msg = "Can't delete machine types yet."
            KMessageBox.information(self, msg)
        else:
            msg = 'Problem with delete - context %s id %s' % (context, ident)
            KMessageBox.error(self, msg)

    def _perform_edit_action(self, context, ident):
        if context == 'Variables':
            self.doc.mtype.edit_variables()
        elif context == 'Scripts':
            self.doc.mtype.edit_script(ident)
        elif context == 'machine_type':
            #KMessageBox.information(self, 'Editing of machine types is unimplemented')
            dialog = BaseRecordDialog(self, ['diskconfig'])
            dialog.context = context
            dialog.mtype = ident
            dialog.connect(dialog, SIGNAL('okClicked()'), self.updateRecord)
            dialog.frame.setText("Edit Machine Type %s" % ident)
            dialog.connect(dialog, SIGNAL('cancelClicked()'),
                                          self._destroy_dialog)
            row = self.doc.mtype.get_row()
            data = {}
            for field in ['diskconfig']:
                if row[field] is not None:
                    data[field] = row[field]
            dialog.setRecordData(data)
            dialog.setButtonOKText('update', 'update')
            self._dialog = dialog
            dialog.show()

        else:
            msg = 'edit context %s id %s is unsupported' % (context, ident)
            KMessageBox.error(self, msg)

    def insertNewRecord(self):
        dialog = self._dialog
        context = dialog.context
        data = dialog.getRecordData()
        if context == 'Families':
            self.doc.mtype.append_family(data['family'])
        elif context == 'Variables':
            self.doc.mtype.append_variable(data['name'],
                                           data['value'])
        elif context == 'machine_type':
            self.doc.mtype.add_new_type(data['name'])
            self.doc.mtype.set_machine_type(data['name'])
        else:
            KMessageBox.error(self, 'Error handling context %s' % context)
        self._dialog = None
        self.resetView()
        
    def updateRecord(self):
        dialog = self._dialog
        context = dialog.context
        data = dialog.getRecordData()
        print data
        if context == 'machine_type':
            newdata = {}
            for field, value in data.items():
                if not value:
                    newdata[field] = None
                else:
                    newdata[field] = value
            self.doc.mtype.update_machine_type(dialog.mtype, newdata)
        self.resetView()
            

    def insertNewScript(self):
        dialog = self._dialog
        data = dialog.getRecordData()
        mtype = self.doc.mtype
        mtype.insert_script(data['name'], strfile(data['data']))
        self._dialog = None
        self.resetView()

    def _destroy_dialog(self):
        del self._dialog
        self._dialog = None
        
