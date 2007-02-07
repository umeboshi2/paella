from useless.kdebase import get_application_pointer
from useless.kdebase.mainwin import BaseMainWindow

from widgets import BasePaellaWidget

class BasePaellaWindow(BaseMainWindow, BasePaellaWidget):
    def initPaellaCommon(self):
        BasePaellaWidget.initPaellaCommon(self)
        
        
