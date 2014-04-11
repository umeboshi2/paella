from qt import QMimeSourceFactory

from kdeui import KTextBrowser

from useless.kdebase import get_application_pointer


import warnings
class MimeSources(QMimeSourceFactory):
    def __init__(self):
        warnings.warn('MimeSources needs more work and needs to be put in a better place',
                      RuntimeWarning, stacklevel=2)
        QMimeSourceFactory.__init__(self)
        self.addFilePath('/usr/share/wallpapers')


class ViewBrowser(KTextBrowser):
    # docclass is meant to be a forgetHTML document class
    # the docclass takes the app as the first argument
    def __init__(self, parent, docclass):
        KTextBrowser.__init__(self, parent)
        self.setMimeSourceFactory()
        self.app = get_application_pointer()
        self.doc = docclass(self.app)
        self.setNotifyClick(True)

    # this should be thought about again
    def setMimeSourceFactory(self, factory=None):
        if factory is None:
            self.mimes = MimeSources()
        else:
            self.mimes = factory
        KTextBrowser.setMimeSourceFactory(self, self.mimes)
            
    # here we are assuming that self.doc has a set_clause method
    def set_clause(self, clause):
       self.doc.set_clause(clause)
       self.setText(self.doc.output())
