from paella.base.classes.dpkg import ConfigObject

from paella.gtk.middle import ListNoteBook
from paella.gtk.middle import TextScroll
from paella.gtk.listboxes import ScrollCList
from paella.gtk.windows import TwinListCndWin
from paella.gtk.windows import CommandBoxWindow
from gtk import mainloop, mainquit, ScrolledWindow

class PackageBrowser(ListNoteBook):
    def __init__(self, config):
        ListNoteBook.__init__(self)
        self.config = config
        self.set_rows(self.config.filelist.keys(), columns = ['package'])
        self.set_row_select(self._package_selected)
        self.append_page(TextScroll('hello there'), 'status')
        for tab in ['conffiles', 'md5sums', 'filelist']:
            self.append_page(ScrollCList(), tab)
        

    def _package_selected(self, *args):
        print args
        print '_package_selected'
        package = args[0].get_selected_data()[0][0]
        print package

        pages = dict(self.pages)
        config = self.config
        pages['filelist'].set_rows(config.filelist[package], [package])
        if self.config.conffiles.has_key(package):
            pages['conffiles'].set_rows(config.conffiles[package], [package])
        else:
            pages['conffiles'].set_rows([], columns=[])
                
        if self.config.md5sums.has_key(package):
            pages['md5sums'].set_rows(config.md5sums[package].items(), ['file', 'md5sum'])
        else:
            pages['md5sums'].set_rows([], columns=[])
        status = '\n'.join(['%s: %s' %(k,v) for k,v in config.status[package].items()])
        pages['status'].set_text(status)
        
        
        #self.set_text(self.config.status[package])
        
class PackageBrowserWindow(CommandBoxWindow):
    def __init__(self, config, name='PackageBrowserWindow'):
        CommandBoxWindow.__init__(self, name=name)
        self.browser = PackageBrowser(config)
        self.config = config
        self.vbox.add(self.browser)
        self.tbar.add_button('hello', 'hello there', self.__hello__)

    def __hello__(self, *args):
        print args
        print 'toolbar buttyon pressed'
        button = args[0]
        print button.get_name()
        print self.tbar.tools

        
def mycancel(*args):
    print args
    print 'cancelled'
    mainquit()
    
if __name__ == '__main__':
    co = ConfigObject()
    #cb = ConfigBrowser(co)
    #pb = PackageBrowser(co)
    #win = CommandBoxWindow()
    #win.vbox.add(pb)
    #ps = re.compile('[\w-]+:')
    #bp = co.status['bash']
    co.set_config()
    pb = PackageBrowserWindow(co)
    

    mainloop()
    #cf = apt_pkg.newConfiguration()#

    #apt_pkg.init()
    
    #cache = apt_pkg.GetCache()
    #sf = open('status.local')
    #pls = parse_dpkg_status('status.local')

