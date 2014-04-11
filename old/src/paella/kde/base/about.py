#from qt import SIGNAL, SLOT, Qt

from kdecore import KAboutData

from kdeui import KMessageBox, KAboutDialog


class AboutData(KAboutData):
    def __init__(self):
        appname = 'paella-management'
        progname = 'paella-management'
        version = '0.7'
        short_desc = "Paella database management"
        KAboutData.__init__(self, appname, progname, version, short_desc)
        
                            
class AboutDialog(KAboutDialog):
    def __init__(self, parent, *args):
        KAboutDialog.__init__(self, parent, *args)
        self.setTitle('Paella Configuration Management Database')
        self.setAuthor('Joseph Rawson')

