from kdeui import KStdAction

from paella.kde.base.mainwin import BasePaellaWindow





class SuiteManagerWindow(BasePaellaWindow):
    def __init__(self, parent, name='SuiteManagerWindow'):
        BasePaellaWindow.__init__(self, parent, name=name)
        self.initPaellaCommon()

    def initActions(self):
        collection = self.actionCollection()
        self.quitAction = KStdAction.quit(self.close, collection)

    def initMenus(self):
        pass

    def initToolbar(self):
        pass
    
