from qt import SIGNAL

from kdeui import KStdAction

from useless.kdebase import get_application_pointer
from useless.kdebase.mainwin import BaseMainWindow

from widgets import BasePaellaWidget

class BasePaellaWindow(BaseMainWindow, BasePaellaWidget):
    def initPaellaCommon(self):
        BasePaellaWidget.initPaellaCommon(self)
        

    def _common_actions_setup(self):
        self.initActions()
        self.initMenus()
        self.initToolbar()
        
class BaseTextEditWindow(BasePaellaWindow):
    def __init__(self, parent, texteditclass, name='BaseTextEditWindow'):
        BasePaellaWindow.__init__(self, parent, name=name)
        self.mainView = texteditclass(self)
        self.connect(self.mainView, SIGNAL('textChanged()'), self.slotTextChanged)
        self.statusBar()
        self.setCentralWidget(self.mainView)
        self._common_actions_setup()
        
    def _status_msg(self, status=None):
        return 'Override _status_msg (status %s)' % status

    def _update_status(self, status=None):
        msg = self._status_msg(status=status)
        self.statusBar().message(msg)
        
    def initActions(self):
        collection = self.actionCollection()
        self.quitAction = KStdAction.quit(self.close, collection)
        self.saveAction = KStdAction.save(self.slotSave, collection)

    def initMenus(self):
        pass

    def initToolbar(self):
        toolbar = self.toolBar()
        self.saveAction.plug(toolbar)
        self.quitAction.plug(toolbar)

    def slotTextChanged(self):
        self._update_status('CHANGED')

    def slotSave(self):
        self._update_status('Saved')

        
