from gtk import Window, Button, Combo, VBox, HBox
from gtk import ScrolledWindow, Entry, Label, Calendar

from gtk import TRUE, FALSE
from simple import HandleToolbar, SimpleMenuBar, SimpleMenu
from simple import RadioMenu
from middle import TwinCList, CommandBox
from helpers import HasMenuBar, HasMenuDialog
mush = '/usr/share/pixmaps/gnome-gmush.png'

class TwinListCndWin(Window):
    def __init__(self):
        Window.__init__(self)
        self.vbox = VBox()
        self.button_box = HBox()
        self.listbox = TwinCList()

        self.vbox.add(self.listbox)
        self.add(self.vbox)
        self.vbox.show()
        self.show()
        self.set_size_request(300, 200)
        self.listbox.set_position(140)


class CommandBoxWindow(Window, HasMenuBar):
    def __init__(self, cbox=None, name='CommandWindow'):
        Window.__init__(self)
        self.set_name(name)
        self.vbox = cbox
        if cbox is None:
            self.vbox = CommandBox()
        self.add(self.vbox)
        self.tbar = self.vbox.tbar
        self.menubar = self.vbox.menubar
        self.show()
        
class MenuWindowOrig(Window):
    def __init__(self, name='MenuVBoxWindow'):
        Window.__init__(self)
        self.set_name(name)
        self.vbox = VBox()
        self.add(self.vbox)
        self.menubar = SimpleMenuBar()
        self.vbox.pack_start(self.menubar, FALSE, FALSE, 0)
        self.vbox.show()
        self.show()

    def add_menu(self, commands, name, function, radio=False):
        if radio:
            new_menu = RadioMenu(commands, function)
        else:
            new_menu = SimpleMenu()
            for command in commands:
                new_menu.add(command, function)
        self.menubar.append(new_menu, name)

class MenuWindow(Window, HasMenuDialog):
    def __init__(self, name='MenuVBoxWindow'):
        Window.__init__(self)
        self.set_name(name)
        self.vbox = VBox()
        self.add(self.vbox)
        self.menubar = SimpleMenuBar()
        self.vbox.pack_start(self.menubar, FALSE, FALSE, 0)
        self.vbox.show()
        self.show()
    

        
            
        
        
