from gtk import TRUE, FALSE
from gtk import SELECTION_MULTIPLE, SELECTION_EXTENDED, SELECTION_SINGLE
from gtk import DEST_DEFAULT_MOTION
from gtk import DEST_DEFAULT_HIGHLIGHT
from gtk import DEST_DEFAULT_DROP
from gtk.gdk import ACTION_COPY, ACTION_MOVE
from gtk.gdk import BUTTON1_MASK, BUTTON_PRESS_MASK
from gtk.gdk import BUTTON2_MASK, BUTTON3_MASK

from gtk import MenuItem, AccelGroup

from paella.base import debug, Error

from base import right_click_pressed
from listboxes import ListBox
from simple import SimpleMenu, ItemEntry

def make_menu(options, function, name='_none_'):
    menu = SimpleMenu()
    menu.set_name(name)
    for option in options:
        menu.add(option, function)
    return menu

def right_click_menu(widget, event, menu):
    debug('menu popper')
    if right_click_pressed(event):
        menu.popup(None, None, None, event.button, event.time)



def populate_menu(mainmenu, section, commands, function):
    new_menu = SimpleMenu()
    section_item = MenuItem(section)
    section_item.set_name(section)
    section_item.show()
    section_item.set_submenu(new_menu)
    mainmenu.append(section_item)
    for command in commands:
        new_menu.add(command, function, section_item)
        

def get_buffer_text(buffer):
    start, end = buffer.get_bounds()
    return buffer.get_text(start, end)


class HasListbox(object):
    def __init__(self, container, name='HasListbox',
		 rcfun=None, dnd=None, targets=[], rcmenu=None):
        object.__init__(self)
        if rcmenu and not rcfun:
            self._rcfun = right_click_menu
        else:
            self._rcfun = rcfun
        self._rcmenu = rcmenu
        self._dnd = dnd
        self.listbox = None
        self.__lb_container__ = container
        self._name = name
        self._targets_ = targets
        
    def set_rows(self, rowlist, columns=[]):
        self.rows = rowlist
        self._make_listbox(self.rows, columns)

    def set_row_select(self, select_fun):
        self.listbox.set_row_select(select_fun)

    def set_right_click(self, function):
        self._rcfun = function
        print '_rcfun', self._rcfun
        
    def _make_listbox(self, rowlist, columns):
        if self.listbox:
            self.listbox.destroy()
            self.listbox=None
        self.listbox = ListBox(rowlist, name=self.get_name(),
                               columns=columns)
        #self.columns = self.listbox._col_titles
        #self.scroll.add_with_viewport(self.listbox)
        self.listbox.set_name(self._name)
        self.__lb_container__.add(self.listbox)
        if self._rcfun:
	    event = 'button_press_event'
	    if self._rcmenu:
		self.listbox.connect(event, self._rcfun, self._rcmenu)
	    else:
		self.listbox.connect(event, self._rcfun)
        if self._dnd:
            self.listbox.connect('drag_data_get', self._dnd)
            self.listbox.drag_source_set(BUTTON1_MASK, self._targets_,
					 ACTION_COPY)
    def drag_rows(self, listbox, context, selection,
                  targettype, time):
        selection.set(selection.target, 0, listbox.get_selected_data())

    def set_select_mode(self, type='single'):
        self.select_state = type
        if type == 'multi':
            self.listbox.set_selection_mode(SELECTION_MULTIPLE)
        elif type == 'extended':
            self.listbox.set_selection_mode(SELECTION_EXTENDED)
        else:
            self.listbox.set_selection_mode(SELECTION_SINGLE)
            
    def get_selected_data(self):
        return self.listbox.get_selected_data()

class HasDialogs(object):
    def destroy_dialog(self, dying):
        name = dying.get_name()
        debug(name, 'dying')
        self.dialogs[name].destroy()
        self.dialogs[name] = None
        


class ItemBrowser(object):
    def reset_rows(self):
        self.set_rows(self.items.select())
        self.set_row_select(self.item_selected)

    def item_selected(self, listbox, row, column, event):
        item = listbox.get_selected_data()[0][0]
        self.current_item = item
        self.__set_pages__(self.current_item)

    def __set_pages__(self, item):
        print 'override me'

    def __set_cursors__(self):
        print 'override me'

    def __close_cursors__(self):
        print 'override me'

    def __make_menu__(self, options, function):
        menu = SimpleMenu()
        for option in options:
            menu.add(option, function)
        return menu


class HasMenuBar(object):
    def __goofy__(self):
        pass

    def add_menu_orig(self, commands, name, function):
        new_menu = SimpleMenu()
        for command in commands:
            new_menu.add(command, function)
        self.menubar.append(new_menu, name)
    def add_menu(self, commands, name, function, radio=False):
        if radio:
            new_menu = RadioMenu(commands, function)
        else:
            new_menu = SimpleMenu()
            for command in commands:
                new_menu.add(command, function)
        self.menubar.append(new_menu, name)

class _HasRecord_(object):
    def __init__(self, vbox, itementry, data, name='HasRecordText'):
        object.__init__(self)
        vbox.set_name(name)
        if type(data) is list:
            self._data_items_ = data
        else:
            self._data_items_ = data.items()
        self.entries = dict([(i[0], itementry(i)) for i in self._data_items_])
        self.accels = AccelGroup()
        for key, value in self._data_items_:
            vbox.pack_start(self.entries[key], FALSE, FALSE, 1)
            self[key] = str(value)
        
    def keys(self):
        return [key for key, value in self._data_items_]

    def values(self):
        return [self[key] for key in self.keys()]

    def items(self):
        return [(key, self[key]) for key in self.keys()]
    
    def update(self, data):
        for k, v in data.items():
            if k in self.keys():
                self[k] = v


            
class HasRecordBox(_HasRecord_):
    def __init__(self, vbox, data, name='HasRecordBox'):
        vbox.set_events(BUTTON3_MASK)
        _HasRecord_.__init__(self, vbox, ItemEntry, data, name=name)

    def __getitem__(self, key):
        return self.entries[key].get()
    
    def __setitem__(self, key, value):
        if value is None:
            value = ''
        self.entries[key].entry.set_text(value)

    def connect_entries(self, signal, function, *args):
        for itementry in self.entries.values():
            itementry.entry.connect(signal, function, itementry, *args)

    def connect_box(self, signal, function, *args):
        self.vbox.connect(signal, function, *args)
        

class HasMenuDialog(HasMenuBar, HasDialogs):
    pass
