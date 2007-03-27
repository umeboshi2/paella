import select

from qt import SIGNAL
from qt import QTimer
from qt import QWidget
from qt import QGridLayout
from qt import QLabel

from qt import QVBoxLayout

from kdeui import KDialogBase
from kdeui import KProgress

from useless.kdebase import get_application_pointer
from useless.kdebase.mainwin import BaseMainWindow

from widgets import LogBrowser

class RunnerWidget(QWidget):
    def __init__(self, parent, umlmachines, name='RunnerWidget'):
        QWidget.__init__(self, parent, name)
        self.app = get_application_pointer()
        self.umlmachines = umlmachines
        self.proc = self.umlmachines.run_machine()
        self._mainbox = QVBoxLayout(self, 5, 7)
        # add label
        self.mainlabel = QLabel(self)
        self.mainlabel.setText('Running Umlmachine %s' % self.umlmachines.current)
        self._mainbox.addWidget(self.mainlabel)
        # add stdout viewer
        logfile = self.umlmachines.stdout_logfile.name
        self.logbrowser = LogBrowser(self, logfile)
        self._mainbox.addWidget(self.logbrowser)
        self.timer = QTimer(self)
        self.connect(self.timer, SIGNAL('timeout()'), self.update_progress)
        self.timer.startTimer(1000)
        
    def update_progress(self):
        #retval = self.proc.poll()
        #print retval
        retval = None
        if retval is not None:
            print retval
            self.close()
            
    
    
class UmlRunnerWindow(BaseMainWindow):
    def __init__(self, parent, umlmachines, name='UmlRunLogWindow'):
        BaseMainWindow.__init__(self, parent, name)
        self.mainView = RunnerWidget(self, umlmachines)
        self.setCentralWidget(self.mainView)
        self.setCaption('Uml Machine %s' % self.mainView.umlmachines.current)
        self.resize(500, 700)
        

