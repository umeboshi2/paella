from os.path import dirname
from paella.base.util import makepaths

from gtk import FileSelection
from gtk import DEST_DEFAULT_MOTION
from gtk import DEST_DEFAULT_HIGHLIGHT
from gtk import DEST_DEFAULT_DROP
from gtk.gdk import ACTION_COPY, ACTION_MOVE
from gtk.gdk import BUTTON_PRESS

def right_click_pressed(event):
    if ((event.type, event.button) == (BUTTON_PRESS, 3)):
        return 1
    else:
        return 0

def middle_click_pressed(event):
    return ((event.type, event.button) == (BUTTON_PRESS, 2))
                                      


class FlavoredTargets(list):
    def __init__(self, start, types, flavors):
        list.__init__(self)
        self.start = start
        self.types = types
        self.flavors = flavors
        index = self.start
        for type in self.types:
            for flavor in self.flavors:
                self.append(('%s-%s' % (type, flavor), 0, index))
                index += 1
        
    def flavor(self, flavor):
        return [x for x in self if x[0].split('-')[1] == flavor]

    def get(self, type, flavor):
        return [x for x in self if x[0].split('-') == [type, flavor]]


def rowpacker(key, rows):
    return '^&^'.join([row[key] for row in rows])

def keysplitter(selection):
    return selection.data.split('^&^')

def populate_menu(mainmenu, section, items):
    new_menu = SimpleMenu()
    section_item = MenuItem(section)
    section_item.set_name(section)
    section_item.show()
    section_item.set_submenu(new_menu)
    mainmenu.append(section_item)
    for item in items:
        new_menu.add(item, self.set_template, section_item)
        
def set_receive_targets(widget, drop_function, dest_targets):
    widget.connect('drag_data_received', drop_function)
    widget.drag_dest_set(DEST_DEFAULT_MOTION |
			 DEST_DEFAULT_HIGHLIGHT |
			 DEST_DEFAULT_DROP,
			 dest_targets, ACTION_COPY)


def select_a_file(action, path, ok_function):
        filesel = FileSelection(title='__select_a_file__')
        filesel.cancel_button.connect('clicked',
                                      lambda x: filesel.destroy())
        makepaths(dirname(path))
        filesel.show()
        filesel.ok_button.connect('clicked', ok_function, filesel)
        filesel.set_data('action', action)
        filesel.set_filename(path)
        return filesel
