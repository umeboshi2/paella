from gtk import Window, Button, Combo, VBox, HBox, HPaned
from gtk import ScrolledWindow, Entry, Label, Calendar, TextView
from gtk import Menu, MenuItem, ItemFactory, AccelGroup
from gtk import HSeparator, VSeparator, MenuBar
from gtk import SeparatorMenuItem, RadioMenuItem
from gtk import TRUE, FALSE, WRAP_WORD
from gtk import TOOLBAR_TEXT, ORIENTATION_HORIZONTAL
from gtk import ORIENTATION_VERTICAL
from gtk import TOOLBAR_CHILD_BUTTON
from gtk import HandleBox, Toolbar, ProgressBar

from paella.base import debug, Error

a_font = "-adobe-helvetica-medium-r-*-*-*-100-*-*-*-*-iso8859-1"

class MyCombo(Combo):
    def __init__(self, a_list=[], activate_fun=None):
        Combo.__init__(self)
        self.set_use_arrows(TRUE)
        if a_list:
            self.fill(a_list)
            self.set("No Value Selected")
        if activate_fun:
            self.entry.connect('activate', activate_fun)
        self.show()

    def fill(self, a_list):
        self.set_popdown_strings(a_list)

    def set(self, a_string):
        self.entry.set_text(a_string)

    def get(self):
        return self.entry.get_text()

    
class ItemButton(HBox):
    def __init__(self, item, name='ItemButton'):
        HBox.__init__(self)
        self.set_name(name)
        self._key_, self._val_ = item
        self.label = Label(self._key_)
        self.button = Button(label=self._val_)
        self.pack_start(self.label,0,0,0)
        self.pack_end(self.button,1,1,5)
        map(lambda x: x.show(), [self.label, self.button])
        self.show()

    def set(self, text):
        self._val_ = text
        self.button.set_label(self._val_)
        
        
class ItemEntry_orig(HBox):
    def __init__(self, item, name='ItemEntry'):
        HBox.__init__(self)
        self.set_name(name)
        self._key_, self._val_ = item
        self.label = Label(self._key_)
        self.entry = Entry()
        self.entry.set_text(self._val_)
        self.pack_start(self.label,0,0,0)
        self.pack_end(self.entry,0,0,0)
        map(lambda x: x.show(), [self.label, self.entry])
        self.show()
        
class ItemLabel(HBox):
    def __init__(self, item, name='ItemLabel'):
        HBox.__init__(self)
        self.set_name(name)
        self._key_, self._val_ = item
        self.label = Label(self._key_)
        self.vlabel = Label(self._val_)
        self.pack_start(self.label,0,0,0)
        self.pack_end(self.vlabel,0,0,0)
        map(lambda x: x.show(), [self.label, self.vlabel])
        self.show()        

class ItemEntry(HBox):
    def __init__(self, item, name='ItemEntry'):
        if len(item) != 2:
            raise Error, 'ItemEntry needs item not %s' %item
        field, value = item
        HBox.__init__(self)
        self.set_name(name)
        self.label = Label(field)
        self.pack_start(self.label, FALSE, FALSE, 0)
        self.entry = Entry()
        self.set(str(value))
        self.pack_end(self.entry, TRUE, TRUE, 0)
        self.label.show()
        self.entry.show()
        self.show()

    def get(self):
        return self.entry.get_text()

    def set(self, value):
        self.entry.set_text(value)

    def fieldname(self):
        return self.label.get_text()

class SimpleMenu(Menu):
    def __init__(self, init={}):
        Menu.__init__(self)
        self._menu_dict = {}
        for label, function in init.items():
            self.add(label, function)
        self.show()
        
    def __call__(self, *args):
        return self

    def __getitem__(self, key):
        return self._menu_dict[key]

    def add(self, label, function, menu=None):
        item = MenuItem(label)
        item.set_name(label)
        self.append(item)
        if menu:
            item.connect('activate', function, label, menu)
        else:
            item.connect('activate', function, label)
        item.show()
        self._menu_dict[label] = item

    def add_separator(self):
        sep = SeparatorMenuItem()
        sep.show()
        self.append(sep)
        #self.reorder_child(sep, len(self._menu_dict.keys()) -1)

class RadioMenu(SimpleMenu):
    def __init__(self, commands, function, menu=None):
        SimpleMenu.__init__(self)
        self.main_item = RadioMenuItem(label=commands[0])
        self._menu_dict[commands[0]] = self.main_item
        for command in commands[1:]:
            item = RadioMenuItem(self.main_item, label=command)
            item.set_name(command)
            self.append(item)
            if menu:
                item.connect('activate', function, command, menu)
            else:
                item.connect('activate', function, command)
            item.show()
            self._menu_dict[command] = item
            
    def add(self, label, function, menu=None):
        item = RadioMenuItem(label=label)
        item.set_name(label)
        self.append(item)
        if menu:
            item.connect('activate', function, label, menu)
        else:
            item.connect('activate', function, label)
        item.show()
        self._menu_dict[label] = item


class SimpleMenuBar(MenuBar):
    def __init__(self):
        MenuBar.__init__(self)
        self.show()
        self._menu_dict = {}

    def append(self, menu, name):
        item = MenuItem(name)
        item.show()
        item.set_submenu(menu)
        MenuBar.append(self, item)
        self._menu_dict[name] = menu
        


class TextScroll(ScrolledWindow):
    def __init__(self, text, font=None, name='TextScroll'):
        ScrolledWindow.__init__(self)
        self.set_name(name)
        self.tview = TextView()
        self.tview.set_name(name)
        self.tbuffer = self.tview.get_buffer()
        self.add(self.tview)
        self.tview.set_editable(0)
        self.tview.set_wrap_mode(WRAP_WORD)
        self.tbuffer.set_text(text)
        self.tview.show()
        self.show()

    def set_text(self, text):
        self.tbuffer.set_text(text)
        
        

class HandleToolbar(HandleBox):
    def __init__(self, name='HandleToolbar'):
        HandleBox.__init__(self)
        self.set_name(name)
        self.toolbar = Toolbar()
        self.toolbar.set_orientation(ORIENTATION_HORIZONTAL)
        self.toolbar.set_style(TOOLBAR_TEXT)
        self.toolbar.set_border_width(3)
        self.add(self.toolbar)
        
        self.toolbar.show()
        self.show()

    def add_button(self, text, tooltip, function):
        self.toolbar.append_item(text, tooltip, text, None, function, text)

    def set_orientation(self, orientation='horizontal'):
        if orientation == 'horizontal':
            self.toolbar.set_orientation(ORIENTATION_HORIZONTAL)
        elif orientation == 'vertical':
            self.toolbar.set_orientation(ORIENTATION_VERTICAL)
        else:
            raise Error, 'bad orientation %s' % orientation

class MyProgress:
    def __init__(self):
        ProgressBar.__init__(self)
        self.show()

        
        
class MyTextView:
    pass


