from gtk import Window, Button, Combo, VBox, HBox, HPaned
from gtk import ScrolledWindow, Entry, Label, Calendar
from gtk import Dialog, Notebook, VPaned
from gtk import TRUE, FALSE
from gtk.gdk import BUTTON_PRESS_MASK

from paella.base import Error
from paella.base.util import indexed_items
from listboxes import ListBox
from helpers import HasListbox, HasRecordBox, HasDialogs
from simple import TextScroll, ItemButton, SimpleMenu, HandleToolbar
from simple import SimpleMenuBar

class ScrolledFieldBox(ScrolledWindow):
    def __init__(self, all_fields, select_fun, name='ScrolledFieldBox'):
        ScrolledWindow.__init__(self)
        self.set_name(name)
        self.vbox = VBox()
        self.vbox.show()
        self.add_with_viewport(self.vbox)
        
class _FieldEntry(HBox):
    def __init__(self, name, default=None):
        HBox.__init__(self)
        self.set_name(name)
        self.label = Label(name)
        self.entry = Entry()
        self.pack_start(self.label, TRUE, TRUE, 0)
        self.add(self.entry)
        self.label.show()
        self.entry.show()
        if default:
            self.set(default)
        self.show()
        
    def set(self, value):
        self.entry.set_text(value)

class FieldEntryVbox(VBox):
    def __init__(self, vdict):
        VBox.__init__(self)
        self.vdict = {}
        for name, value in vdict.items():
            self.vdict[name] = _FieldEntry(name, default=value)
            self.add(self.vdict[name])
            self.vdict[name].show()
        self.show()

    def __getitem__(self, key):
        return self.vdict[key]
    def __setitem__(self, key, value):
        if self.vdict.has_key(key):
            self.vdict[key].set(value)
        else:
            raise Error, 'foobar'
    def keys(self):
        return self.vdict.keys()
    def values(self):
        return self.vdict.values()
    def items(self):
        return self.vdict.items()

    def _data_dict(self):
        pass

class ItemButtonBox(VBox):
    def __init__(self, vdict, name='ItemButtonBox'):
        VBox.__init__(self)
        self.set_name(name)
        self.vdict = {}
        for item in vdict.items():
            sname = item[0]
            self.vdict[sname] = ItemButton(item, name='_'.join([name, sname]))
            self.add(self.vdict[sname])
            self.vdict[sname].show()
        self.show()

    def __getitem__(self, key):
        return self.vdict[key]
    def __setitem__(self, key, value):
        if self.vdict.has_key(key):
            self.vdict[key].set(value)
        else:
            raise Error, 'foobar'
    def keys(self):
        return self.vdict.keys()
    def values(self):
        return self.vdict.values()
    def items(self):
        return self.vdict.items()

    def _data_dict(self):
        pass
    
    

class TwinCList(HPaned):
    def __init__(self, name='TwinCList'):
        HPaned.__init__(self)
        self.set_name(name)
        self.Lbox = ListBox([], name='%s-left' %name, columns=[])
        self.Rbox = ListBox([], name='%s-right' %name, columns=[])
        self.add1(self.Lbox)
        self.add2(self.Rbox)
        self.show()

    def Lfill(self, rows, columns):
        self.Lbox.destroy()
        self.Lbox = ListBox(rows, name='left', columns=columns)
        self.add1(self.Lbox)

    def Rfill(self, rows, columns):
        self.Rbox.destroy()
        self.Rbox = ListBox(rows, name='right', columns=columns)
        self.add1(self.Rbox)


class _LeftListView(HPaned, HasListbox, HasDialogs):
    def __init__(self, name='_LeftListView'):
        HPaned.__init__(self)
        self.set_name(name)
        self.scroll = ScrolledWindow()
        self.add1(self.scroll)
        self.scroll.show()
        if hasattr(self, 'menu'):
            HasListbox.__init__(self, self.scroll, rcmenu=self.menu)
        else:
            HasListbox.__init__(self, self.scroll)
        self.set_size_request(300,200)
        self.set_position(140)
        self.show()

class _TopListView(VPaned, HasListbox, HasDialogs):
    def __init__(self, name='_LeftListView'):
        VPaned.__init__(self)
        self.set_name(name)
        self.scroll = ScrolledWindow()
        self.add1(self.scroll)
        self.scroll.show()
        if hasattr(self, 'menu'):
            HasListbox.__init__(self, self.scroll, rcmenu=self.menu)
        else:
            HasListbox.__init__(self, self.scroll)
        self.set_size_request(300,200)
        self.set_position(140)
        self.show()

class ListTextView(_LeftListView):
    def __init__(self, name='ListTextVies'):
        _LeftListView.__init__(self, name=name)
        self.text_area = TextScroll('hello')
        self.add2(self.text_area)

    def set_text(self, text):
        self.text_area.set_text(text)

class MyNotebook(Notebook):
    def __init__(self):
        Notebook.__init__(self)
        self.show()
        self._pages = []
        self._set_pages()

    def _set_pages(self):
        self.pages = dict(self._pages)

    def append_page(self, child, label):
        self._pages.append((label, child))
        Notebook.append_page(self, child, Label(label))
        self._set_pages()
                          
    def remove_page(self, name):
        number = indexed_items(self._pages)[name]
        Notebook.remove_page(self, number)
        del self._pages[number]
        self._set_pages()
        
    def current_page(self):
        return self._pages[Notebook.get_current_page(self)]

    def set_current_page(self, name):
        number = indexed_items(self._pages)[name]
        Notebook.set_current_page(self, number)

        
class ListNoteBook(_LeftListView):
    def __init__(self, name='ListNoteBook'):
        _LeftListView.__init__(self, name=name)
        self.nbook = MyNotebook()
        self.add2(self.nbook)
        self.pages = self.nbook.pages
        
    def append_page(self, child, name):
        self.nbook.append_page(child, name)
        self.pages = self.nbook.pages
        
    def remove_page(self, name):
        self.nbook.remove_page(name)
        self.pages = self.nbook.pages

    def current_page(self):
        return self.nbook.current_page()

    def set_current_page(self, name):
        self.nbook.set_current_page(name)
        self.pages = self.nbook.pages
        

class ListAboveNoteBook(_TopListView):
    def __init__(self, name='ListNoteBook'):
        _TopListView.__init__(self, name=name)
        self.nbook = Notebook()
        self.add2(self.nbook)
        self.nbook.show()
        self.pages = []

    def append_page(self, child, label):
        self.pages.append((label, child))
        self.nbook.append_page(child, Label(label))

    def remove_page(self, name):
        print self.pages
        number = indexed_items(self.pages)[name]
        self.nbook.remove_page(number)
        del self.pages[number]

        
class TextTemplater(TextScroll):
    def __init__(self, text, font=None, name='TextTemplater'):
        TextScroll.__init__(self, text, font=font, name=name)
        #self.tview.set_editable(0)

class HasMenuBar(object):
    def __goofy__(self):
        pass

    def add_menu(self, commands, name, function):
        new_menu = SimpleMenu()
        for command in commands:
            new_menu.add(command, function)
        self.menubar.append(new_menu, name)
        
class ScrollCList(ScrolledWindow, HasListbox):
    def __init__(self, rows=[], name='ScrollCList',
                 columns=[], **args):
        ScrolledWindow.__init__(self)
        HasListbox.__init__(self, self, name=name, **args)
        self.show()

class RecordBox(ScrolledWindow, HasRecordBox):
    def __init__(self, data, name='RecordBox'):
        ScrolledWindow.__init__(self)
        self.set_name(name)
        self.vbox = VBox()
        self.add_with_viewport(self.vbox)
        HasRecordBox.__init__(self, self.vbox, data, name=name)
        self.vbox.show()
        self.show()
        self.vbox.set_events(BUTTON_PRESS_MASK)

class CommandBox(VBox, HasMenuBar):
    def __init__(self, name='CommandBox'):
        VBox.__init__(self)
        self.set_name(name)
        self.tbar = HandleToolbar()
        self.menubar = SimpleMenuBar()
        self.pack_start(self.menubar, FALSE, FALSE, 0)
        self.pack_end(self.tbar, FALSE, FALSE, 0)
        self.show()

class TwinScrollCList(HPaned):
    def __init__(self, name='TwinScrollCList'):
        HPaned.__init__(self)
        self.set_name(name)
        self.lbox = ScrollCList()
        self.rbox = ScrollCList()
        self.add1(self.lbox)
        self.add2(self.rbox)
        self.show()
        
if __name__ == '__main__':
    import paella.gtk
    from gtk import mainloop, mainquit
    from paella.base.util import file2str
    from gtk import Window
    tt = TextTemplater(file2str('/etc/debconf.conf'))
    win = Window()
    win.add(tt)
    win.show()
    win.connect('destroy', mainquit)
    mainloop()
