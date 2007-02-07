#from qt import SIGNAL, SLOT, Qt

from kdecore import KAboutData

from kdeui import KMessageBox, KAboutDialog


class AboutData(KAboutData):
    def __init__(self):
        appname = 'paella-kde-umlmanager'
        progname = 'paella-kde-umlmanager'
        version = '0.7'
        short_desc = "Paella user mode linux management"
        KAboutData.__init__(self, appname, progname, version, short_desc)
        
                            
class AboutDialog(KAboutDialog):
    def __init__(self, parent, *args):
        KAboutDialog.__init__(self, parent, *args)
        self.setTitle('Paella Usermode Linux Manager')
        self.setAuthor('Joseph Rawson')

