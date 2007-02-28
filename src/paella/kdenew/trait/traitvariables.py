from qt import SIGNAL
from qt import QScrollView

from kdeui import KStdAction

from paella.db.trait.relations import TraitParent, TraitEnvironment

from paella.kdenew.base.mainwin import BasePaellaWindow
from paella.kdenew.base.recordedit import BaseVariablesEditor
from paella.kdenew.base.dialogs import NewTraitVariableDialog

class TraitVariablesEditor(BaseVariablesEditor):
    def __init__(self, parent, suite, trait, name='TraitVariablesEditor'):
        BaseVariablesEditor.__init__(self, parent, [], name='TraitVariablesEditor')
        self.traitenv = TraitEnvironment(self.conn, suite, trait)
        fields = self.traitenv.keys()
        fields.sort()
        data = dict(self.traitenv.items())
        self.set_fields(fields, data=data)
        self.resize(500, 600)

    def reset_grid(self):
        data = dict(self.traitenv.items())
        fields = data.keys()
        fields.sort()
        self.set_fields(fields, data)
        
class TraitVariablesWindow(BasePaellaWindow):
    def __init__(self, parent, suite, trait, name='TraitVariablesWindow'):
        BasePaellaWindow.__init__(self, parent, name=name)
        self.resize(500, 600)
        self.initPaellaCommon()
        self.mainView = QScrollView(self, 'TraitVariablesScrollView')
        self.tveditor = TraitVariablesEditor(self.mainView, suite, trait)
        self.mainView.addChild(self.tveditor)
        self.setCentralWidget(self.mainView)
        self.mainView.setResizePolicy(self.mainView.AutoOneFit)
        self.initActions()
        self.initMenus()
        self.initToolbar()
        
    def initActions(self):
        collection = self.actionCollection()
        self.quitAction = KStdAction.quit(self.close, collection)
        self.saveAction = KStdAction.save(self.slotSave, collection)
        self.newAction = KStdAction.openNew(self.slotNew, collection)
        
    def initMenus(self):
        pass
    
    def initToolbar(self):
        toolbar = self.toolBar()
        self.newAction.plug(toolbar)
        self.saveAction.plug(toolbar)
        self.quitAction.plug(toolbar)

    def _varline(self, var):
        return '%s\n' % var
    
    def _changed_report(self, removed, added, changed):
        if removed or added or changed:
            msg = 'Changes to Trait Variables:\n'
            if removed:
                msg += 'Removed:\n\n'
                for var in removed:
                    msg += self._varline(var)
            if added:
                msg += 'Added:\n\n'
                for var in added:
                    msg += self._varline(var)
            if changed:
                msg += 'Changed:\n\n'
                for var in changed:
                    msg += self._varline(var)
        else:
            msg  = 'No Changes'
        return msg
        
    def slotSave(self):
        newdata = self.tveditor.get_data()
        oldata = dict(self.tveditor.traitenv.items())
        removed = [k for k in oldata if k not in newdata]
        added = [k for k in newdata if k not in oldata]
        changed = [k for k in newdata if newdata[k] != oldata[k]]
        report = self._changed_report(removed, added, changed)
        from kdeui import KMessageBox
        KMessageBox.information(self, report)
        

    def slotNew(self):
        win = NewTraitVariableDialog(self)
        win.show()
        win.connect(win, SIGNAL('okClicked()'), self.newVariableSelected)
        self._dialog = win
        
    def newVariableSelected(self):
        win = self._dialog
        data = win.getRecordData()
        self.tveditor.traitenv[data['name']] = data['value']
        #self.tveditor.reset_grid()
        self.tveditor.add_field(data['name'], value=data['value'])
        #print data
        #from kdeui import KMessageBox
        #KMessageBox.information(self, str(data))
