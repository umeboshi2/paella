import os
from ConfigParser import RawConfigParser

from useless.base import Error, debug
from useless.base.config import Configure, list_rcfiles

from useless.gtk import dialogs
from useless.gtk.simple import TextScroll
from useless.gtk.middle import ListNoteBook

from gtk import mainloop, mainquit


#from paella.uml.umlrunner import get_machines_config

SYSOPTS = ['config_path', 'mirrors', 'freespace', 'workspace',
           'script_path']
           
MAINOPTS = ['db_bkup_path', 'template_path', 'python_path', 'rootimage_path',
            'tun_iface', 'tun_netmask', 'umlkernver', 'uml_socket', 'nfs_host',
            'bkuptarball_path', 'base_path']
MACHOPTS = ['profile', 'basefile']

DBOPTS = ['dbhost', 'dbname', 'dbusername', 'dbpassword']
UMLOPTS = ['con0', 'eth0', 'con1', 'mem', 'con']
XUMLOPTS = ['paellarc']

ALLOPTS = SYSOPTS + DBOPTS + MAINOPTS + MACHOPTS + UMLOPTS + XUMLOPTS


def get_machines_config():
    paellarc = Configure(list_rcfiles('paellarc'))
    umcfg = paellarc.get('umlmachines', 'uml_machines_conf')
    cfg = RawConfigParser()
    cfg.read(umcfg)
    return Configure([umcfg])

def _itemline(key, value):
    return '%s:  %s' % (key, value)

def _itemlines(parser, section, options, raw=False):
    return [_itemline(opt, parser.get(section, opt, raw)) for opt in options]


class MachineBrowser(ListNoteBook):
    def __init__(self, cfg):
        ListNoteBook.__init__(self)
        self.cfg = cfg
        #self.menu = make_menu
        self.reset_rows()

    def reset_rows(self, *args):
        print 'reset_rows'
        self.set_rows(self.cfg.sections(), ['uml machine'])
        self.set_row_select(self.machine_selected)

    def machine_selected(self, listbox, row, column, event):
        machine = listbox.get_selected_data()[0][0]
        print 'machine selected', machine
        text = TextScroll(self._print_items(machine))
        if machine not in self.pages:
            self.append_page(text, machine)
        self.set_current_page(machine)
        
    def _print_items(self, machine, raw=True):
        slines = _itemlines(self.cfg, machine, SYSOPTS, raw=raw)
        dblines = _itemlines(self.cfg, machine, DBOPTS, raw=raw)
        mnlines = _itemlines(self.cfg, machine, MAINOPTS, raw=raw)
        mclines = _itemlines(self.cfg, machine, MACHOPTS, raw=raw)
        umlines = _itemlines(self.cfg, machine, UMLOPTS, raw=raw)
        xumlines = _itemlines(self.cfg, machine, XUMLOPTS, raw=raw)
        alllines = [slines, dblines, mnlines, mclines, umlines, xumlines]
        sep = '\n\n------------------\n\n'
        text = sep.join(['\n'.join(lines) for lines in alllines]) + '\n'
        return text
    
        
if __name__ == '__main__':
    from gtk import Window
    cfg = get_machines_config()
    sections = cfg.sections()
    print sections
    #d.set_rows([dict(section=x) for x in sections])
    m = MachineBrowser(cfg)
    win = Window()
    win.add(m)
    win.show()
    win.connect('destroy', mainquit)
    mainloop()
    
