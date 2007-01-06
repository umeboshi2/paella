from useless.kdebase import get_application_pointer
from useless.kdebase.mainwin import BaseMainWindow

class BasePaellaWindow(BaseMainWindow):
    def initPaellaCommon(self):
        self.app = get_application_pointer()
        self.conn = self.app.conn
        self.cfg = self.app.cfg
        
        
