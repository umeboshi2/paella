from qt import SIGNAL
from qt import QTimer

from kdeui import KTextBrowser

from useless.base.util import shell
from useless.base.path import path

#from useless.kdebase import get_application_pointer


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
        self.logfilename = path(logfile)
        if not self.logfilename.exists():
            shell('touch %s' % self.logfilename)
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
        return self.logfilename.stat().st_size
    
    
    def check_logfile_updated(self):
        return self.logfile_size != self._get_logfile_size()
        
        
