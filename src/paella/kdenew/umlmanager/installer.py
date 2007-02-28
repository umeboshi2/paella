import os
import select

from qt import SIGNAL
from qt import QTimer
from qt import QWidget
from qt import QGridLayout
from qt import QLabel

from kdeui import KTextBrowser
from kdeui import KDialogBase
from kdeui import KProgress

from useless.kdebase import get_application_pointer
from paella.installer.base import CurrentEnvironment

class BaseLogBrowser(KTextBrowser):
    def __init__(self, parent, name='BaseLogBrowser'):
        KTextBrowser.__init__(self, parent, name)
        self.setTextFormat(self.LogText)
        self.timer = QTimer(self)
        self.connect(self.timer, SIGNAL('timeout()'), self.update_logtext)
        self.resume_logging()
        
    def pause_logging(self):
        self.timer.stop()

    def resume_logging(self):
        self.timer.start(500)
        
    def update_logtext(self):
        raise NotImplementedError
    
class StdOutBrowser(BaseLogBrowser):
    def __init__(self, parent, name='StdOutBrowser'):
        BaseLogBrowser.__init__(self, parent, name=name)
        self.pause_logging()
        self.setVScrollBarMode(self.AlwaysOff)
        
        
class LogBrowser(BaseLogBrowser):
    def __init__(self, parent, logfile, name='LogBrowser'):
        BaseLogBrowser.__init__(self, parent, name=name)
        self.logfilename = logfile
        if not os.path.exists(self.logfilename):
            os.system('touch %s' % self.logfilename)
        self.logfile_size = 0
        self.setVScrollBarMode(self.AlwaysOff)

    def update_logtext(self):
        height = self.contentsHeight()
        self.setContentsPos(0, height)
        if self.check_logfile_updated():
            self.logfile_size = self._get_logfile_size()
            text = file(self.logfilename).read()
            self.setText(text)
                    
    def _get_logfile_size(self):
        s = os.stat(self.logfilename)
        return s.st_size
    
    def check_logfile_updated(self):
        return self.logfile_size != self._get_logfile_size()
        
        
class InstallerWidget(QWidget):
    def __init__(self, parent, umlmachines, name='InstallerWidget'):
        QWidget.__init__(self, parent, name)
        self.resize(600, 600)
        self.app = get_application_pointer()
        self.conn = self.app.conn
        self.umlmachines = umlmachines
        self.machine = self.umlmachines.current
        self.current_machine_process = 'start'
        self.current_profile = None
        self.current_trait = None
        self.traitlist = []
        self.curenv = CurrentEnvironment(self.conn, self.machine)
        self.curenv['current_profile'] = 'None'
        self.curenv['current_trait'] = 'None'
        self.curenv['current_machine_process'] = self.current_machine_process
        self.timer = QTimer(self)
        self.connect(self.timer, SIGNAL('timeout()'), self.update_progress)
        self.timer.startTimer(1000)
        self.grid = QGridLayout(self, 4, 1, 5, 7)
        self.main_label = QLabel(self)
        self.main_label.setText(self._msg())
        self.grid.addWidget(self.main_label, 0, 0)
        self.profile_progress_lbl = QLabel(self)
        self.grid.addWidget(self.profile_progress_lbl, 1, 0)
        self.profile_progress = KProgress(self)
        self.grid.addWidget(self.profile_progress, 2, 0)
        self.logview = LogBrowser(self, '/tmp/uml-installer.log')
        self.grid.addWidget(self.logview, 3, 0)
        #self.console_view = StdOutBrowser(self)
        #self.console_view = KTextBrowser(self)
        #self.grid.addWidget(self.console_view, 4, 0)
        self.console_text = ''
        

    def _msg(self):
        return 'Installing uml machine %s - %s' % (self.machine, self.current_machine_process)

    def update_console_text(self):
        if self.umlmachines.run_process is not None:
            stdout = self.umlmachines.run_process.stdout
            stdoutfd = stdout.fileno()
            ready = select.select([stdoutfd], [], [])
            while stdoutfd in ready[0]:
                line = stdout.readline()
                if line:
                    self.console_text += line
                ready = select.select([stdoutfd], [], [])
            stdout = self.umlmachines.run_process.stdout
            line = stdout.readline()
            if line:
                self.console_text += line
            self.console_view.setText(self.console_text)

        
    def update_progress(self):
        #self.update_console_text()
        process = self.curenv['current_machine_process']
        #print 'update_progress', process
        if process != self.current_machine_process:
            self.current_machine_process = process
            self.main_label.setText(self._msg())
        if self.current_profile is None:
            profile = self.curenv['current_profile']
            if profile != 'None':
                self.current_profile = profile
                print 'profile set to', profile
                traitlist = self.curenv['traitlist']
                tl = [t.strip() for t in traitlist.split(',')]
                self.traitlist = tl
                self.profile_progress.setTotalSteps(len(self.traitlist))
        else:
            trait = self.curenv['current_trait']
            if trait != 'None':
                trait_process = self.curenv['current_trait_process']
                profile = self.current_profile
                msg = 'Installing profile %s, trait %s, process %s' % (profile, trait, trait_process)
                self.profile_progress_lbl.setText(msg)
                self.profile_progress.setProgress(self.traitlist.index(trait) + 1)
                self.app.processEvents()
            
        
class LogBrowserWindow(KDialogBase):
    def __init__(self, parent, machine, name='LogBrowserWindow'):
        KDialogBase.__init__(self, parent, name)
        self.resize(600, 600)
        #self.mainView = LogBrowser(self, '/tmp/uml-installer.log')
        self.mainView = InstallerWidget(self, machine)
        self.setMainWidget(self.mainView)
        self.setButtonOKText('pause log')
        self.setButtonApplyText('resume log')
        
    def slotOk(self):
        print 'Ok pressed'
        self.mainView.logview.pause_logging()

    def slotApply(self):
        print 'Apply pressed'
        self.mainView.logview.resume_logging()
        
