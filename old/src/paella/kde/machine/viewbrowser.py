from qt import SIGNAL
from kdeui import KMessageBox

from useless.base.util import strfile
from useless.kdebase import get_application_pointer
from useless.kdebase.dialogs import BaseRecordDialog

from paella.kde.base import split_url
from paella.kde.base.viewbrowser import ViewBrowser

# import document objects
from paella.kde.docgen.machine import MachineDoc
from paella.kde.docgen.machine import DiskConfigDoc
from paella.kde.docgen.machine import KernelDoc

from base import NewMachineDialog
from base import EditMachineDIalog
from base import NewMachineScriptDialog
from base import NewDiskConfigDialog
from base import BaseMachineAttributeDialog
from base import MachineParentDialog
from base import NewKernelDialog


def pipesplit(stringvalue):
    return stringvalue.split('||')

def split_ident(ident):
    return pipesplit(ident)

class HasDialog(object):
    def __init__(self):
        self._dialog = None
        
    def makeGenericDialog(self, dialog_class, args, show=True):
        if self._dialog is None:
            dialog = dialog_class(self, *args)
            dialog.connect(dialog, SIGNAL('cancelClicked()'), self._destroy_dialog)
            self._dialog = dialog
            dialog.show()
            return dialog
        raise RuntimeError , 'Previous dialog still present.'
        
    def _destroy_dialog(self):
        del self._dialog
        self._dialog = None
        
    
class KernelView(ViewBrowser, HasDialog):
    def __init__(self, parent):
        ViewBrowser.__init__(self, parent, KernelDoc)
        HasDialog.__init__(self)
        self.refresh_view()
        self.kernels = self.doc.kernels
        
    def setSource(self, url):
        url = str(url)
        action, context, ident = pipesplit(url)
        #KMessageBox.information(self, '%s %s %s' % (action, context, ident))
        if action == 'delete':
            self.kernels.delete_kernel(ident)
            self.refresh_view()
        elif action == 'new':
            dlg = self.makeGenericDialog(NewKernelDialog, (self.kernels,))
            dlg.connect(dlg, SIGNAL('okClicked()'), self.new_kernel_selected)
        else:
            KMessageBox.information(self, 'unknown action %s' % action)
            
    def new_kernel_selected(self):
        self._destroy_dialog()
        self.refresh_view()

    def refresh_view(self):
        self.doc.refresh_page()
        self.setText(self.doc.output())
        
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
    
            
class MachineView(ViewBrowser, HasDialog):
    def __init__(self, parent):
        ViewBrowser.__init__(self, parent, MachineDoc)
        HasDialog.__init__(self)
        self._context_methods = dict(Scripts=self._script_context,
                                     Variables=self._variable_context,
                                     Families=self._family_context,
                                     machine=self._machine_context,
                                     parent=self._parent_context)

    def set_machine(self, machine):
        self.doc.set_machine(machine)
        self.setText(self.doc.output())

    def resetView(self):
        machine = self.doc.machine.current_machine
        if machine is None:
            self.setText('')
        else:
            self.set_machine(machine)

    #########################
    # url handling
    #########################
    def setSource(self, url):
        action, context, ident = split_url(url)
        print "in setSource, url is", url
        print "in setSource, context is", context
        if context in self._context_methods:
            self._context_methods[context](action, ident)
        elif context.startswith('attribute||'):
            attribute = pipesplit(context)[1]
            self._attribute_context(attribute, action, ident)
        else:
            KMessageBox.information(self, "unable to handle %s context" % context)
        return
        
    def _unhandled_action(self, action, context):
        msg = 'unable to handle %s action for %s' % (action, context)
        KMessageBox.information(self, msg)
            
    def _script_context(self, action, ident):
        print "context is script", action, ident
        if action == 'new':
            dialog = self.makeGenericDialog(NewMachineScriptDialog, ())
            dialog.connect(dialog, SIGNAL('okClicked()'), self.insertNewScript)
        elif action == 'edit':
            handler = self.doc.machine
            handler.relation.edit_script(ident)
        elif action == 'delete':
            handler = self.doc.machine
            msg = "Really delete the %s script?" % ident
            answer = KMessageBox.questionYesNo(self, msg)
            if answer == KMessageBox.Yes:
                handler.relation.scripts.delete_script(ident)
                self.resetView()
        else:
            self._unhandled_action(action, 'scripts')
            
    def _variable_context(self, action, ident):
        print "context is variable", action, ident
        if action == 'new':
            message = "Add a new variable."
            context = 'variable'
            self.makeNewRecordDialog(context,
                                     ['trait', 'name', 'value'], message)
        elif action == 'delete':
            print "delete variable", ident
            trait, name = split_ident(ident)
            msg = "Really delete this variable: \n"
            msg += "Trait: %s\nName: %s\n" % (trait, name)
            answer = KMessageBox.questionYesNo(self, msg)
            if answer == KMessageBox.Yes:
                handler = self.doc.machine
                handler.relation.environment.delete_variable(trait, name)
                self.resetView()
        elif action == 'edit':
            handler = self.doc.machine
            handler.edit_variables()
            self.resetView()
        else:
            self._unhandled_action(action, 'variables')

    def _family_context(self, action, ident):
        print "context is family", action, ident
        if action == 'new':
            message = "Add a new family."
            context = 'family'
            self.makeNewRecordDialog(context, ['family'], message)
        elif action == 'delete':
            handler = self.doc.machine
            handler.relation.family.delete_family(ident)
            self.resetView()
        else:
            self._unhandled_action(action, 'families')
        
    def _machine_context(self, action, ident):
        handler = self.doc.machine
        if action == 'new':
            dialog = self.makeGenericDialog(NewMachineDialog, (handler,))
            dialog.connect(dialog, SIGNAL('okClicked()'), self.reset_manager)
        elif action == 'edit':
            dialog = self.makeGenericDialog(EditMachineDIalog, (handler, ident))
        elif action == 'delete':
            msg = "Really delete this machine: %s?" % ident
            answer = KMessageBox.questionYesNo(self, msg)
            if answer == KMessageBox.Yes:
                #KMessageBox.information(self, "I'm supposed to be deleting %s" % ident)
                handler.delete_machine(ident)
                self.reset_manager()
        else:
            self._unhandled_action(action, 'machines')

        print "context is machine", action, ident

    def _attribute_context(self, attribute, action, ident):
        print "context is attribute", attribute, action, ident
        handler = self.doc.machine
        if action == 'select':
            dialog = self.makeGenericDialog(BaseMachineAttributeDialog,
                                            (handler, attribute))
            dialog.connect(dialog, SIGNAL('okClicked()'), self._destroy_dialog)
            dialog.connect(dialog, SIGNAL('okClicked()'), self.resetView)
        elif action == 'delete':
            handler.set_attribute(attribute, None)
            self.resetView()
        else:
            self._unhandled_action(action, '%s context' % attribute)

    def _parent_context(self, action, ident):
        handler = self.doc.machine
        if action == 'select':
            dialog = self.makeGenericDialog(MachineParentDialog,
                                            (handler,))
            dialog.connect(dialog, SIGNAL('okClicked()'), self.slotParentSelected)
        elif action == 'delete':
            if handler.relation.parents.has_children(ident):
                msg = "This machine has children.\n"
                msg += "Removing this parent may affect the children.\n"
                msg += "Do you wish to remove it anyway?"
                answer = KMessageBox.questionYesNo(self, msg)
                if answer == KMessageBox.Yes:
                    handler.delete_parent()
            else:
                handler.delete_parent()
            self.resetView()
        else:
            self._unhandled_action(action, 'parent')




    
    #########################
    # slots / actions
    #########################
    def insertNewScript(self):
        dialog = self._dialog
        data = dialog.getRecordData()
        handler = self.doc.machine
        scriptname = data['name']
        scriptfile = strfile(data['data'])
        handler.relation.scripts.insert_script(scriptname, scriptfile)
        self._destroy_dialog()
        self.resetView()

    def slotParentSelected(self):
        dialog = self._dialog
        parent = str(dialog.parentEntry.text())
        handler = self.doc.machine
        handler.set_parent(parent)
        self._destroy_dialog()
        self.resetView()
        
    def insertNewRecord(self):
        handler = self.doc.machine
        dialog = self._dialog
        context = dialog.context
        data = dialog.getRecordData()
        if context == 'family':
            family = data['family'].strip()
            handler.relation.family.append_family(family)
        elif context == 'variable':
            trait = data['trait'].strip()
            name = data['name'].strip()
            value = data['value'].strip()
            handler.relation.environment.append_variable(trait, name, value)
        else:
            msg = 'unhandled insertNewRecord, context is %s' % context
            KMessageBox.information(self, msg)
        self._destroy_dialog()
        self.resetView()
        print "in insertNewRecord, context is", context

    def makeNewRecordDialog(self, context, fields, message):
        dialog = self.makeGenericDialog(BaseRecordDialog, (fields,))
        dialog.context = context
        dialog.connect(dialog, SIGNAL('okClicked()'), self.insertNewRecord)
        dialog.frame.setText(message)


    def reset_manager(self):
        mainwindow = self.parent().parent()
        mainwindow.slotManagemachine()
