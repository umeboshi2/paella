from gtk import Window, VBox, HBox, AccelGroup
from gtk import ScrolledWindow, Label, Calendar
from gtk import Dialog as gtkDialog
from gtk import Entry as gtkEntry
from gtk import Combo as gtkCombo
from gtk import Button

from gtk import TRUE, FALSE

from simple import TextScroll, ItemEntry
from helpers import HasListbox, HasRecordBox

class _labelentry(ItemEntry):
    def __init__(self, field, value='', name='_labelentry'):
        ItemEntry.__init__(self, (field, value), name=name)
        
class _GenDialog(gtkDialog):
    def __init__(self, name='GenDialog'):
        gtkDialog.__init__(self)
        self.set_name(name)
        self.ok_button = Button('ok', 'gtk-ok')
        self.ok_button.set_name(name)
        self.cancel_button = Button('cancel', 'gtk-cancel')
        self.cancel_button.set_name(name)
        self.action_area.pack_start(self.ok_button, TRUE, TRUE, 0)
        self.action_area.pack_end(self.cancel_button, TRUE, TRUE, 0)
        self.ok_button.show()
        self.cancel_button.show()
        self.cancel_button.connect('clicked', lambda *x : self.destroy())
        self._buttons_ = {}
        self.show()

    def set_ok(self, ok_fun):
        self.ok_button.connect('clicked', ok_fun)

    def set_cancel(self, cancel_fun):
        self.cancel_button.connect('clicked', cancel_fun)
        self.connect('destroy', cancel_fun)

    def add_button(self, name, func, label='foo'):
        if name not in self._buttons_.keys():
            self._buttons_[name] = Button(label)
            self._buttons_[name].show()
            self._buttons_[name].connect('clicked', func)
            self.action_area.add(self._buttons_[name])
            
class Dialog(_GenDialog):
    def __init__(self, message, name='Dialog'):
        _GenDialog.__init__(self, name=name)
        self.set_name(name)
        self.label = Label(message)
        self.vbox.pack_start(self.label, FALSE, TRUE, 0)
        self.vbox.set_homogeneous(FALSE)
        self.label.show()

class Message(Dialog):
    def __init__(self, message):
        Dialog.__init__(self, message)
        self.ok_button.connect('clicked', lambda *x : self.destroy())
        
class Calendar(_GenDialog):
    def __init__(self):
        _GenDialog.__init__(self)
        self.calendar = Calendar()
        self.vbox.pack_start(self.calendar, TRUE, TRUE, 0)
        self.calendar.show()

    def get_date(self):
        return self.calendar.get_date()

    def get_strdate(self):
        y,m,d = self.calendar.get_date()
        return '%s-%s-%s' %(y, m+1, d)

class Entry(Dialog):
    def __init__(self, message, name='entry'):
        Dialog.__init__(self, message, name=name)
        self.set_name(name)
        self.entry = gtkEntry()
        self.accels = AccelGroup()
        self.vbox.pack_start(self.entry, TRUE, TRUE, 0)
        self.entry.show()

    def get(self):
        return self.entry.get_text()

    def set(self, text):
        self.entry.set_text(text)

    def set_ok(self, ok_fun):
        Dialog.set_ok(self, ok_fun)
        self.entry.connect('activate', ok_fun)
        self.entry.add_accelerator('activate', self.accels, 0x07a, 0, 0)

class RecordEntry(Dialog, HasRecordBox):
    def __init__(self, message, data, name='RecordEntry'):
        Dialog.__init__(self, message, name=name)
        HasRecordBox.__init__(self, self.vbox, data, name=name)


    def set_ok(self, ok_fun):
        Dialog.set_ok(self, ok_fun)
        for entry in [x.entry for x in self.entries.values()]:
            entry.connect('activate', ok_fun)
            entry.add_accelerator('activate', self.accels, 0x07a, 0, 0)


class CList(Dialog, HasListbox):
    def __init__(self, message, name='MyCListDialog',
                 dnd=None, targets=[]):
        Dialog.__init__(self, message, name=name)
        self.set_name(name)
        self.scroll = ScrolledWindow()
        HasListbox.__init__(self, self.scroll, name=name,
                            dnd=dnd, targets=targets)
        self.scroll.show()
        self.vbox.pack_start(self.scroll, TRUE, TRUE, 0)
        self.set_size_request(150, 300)
            
class TextDialog(Dialog):
    def __init__(self, message, text, name='TextDialog'):
        Dialog.__init__(self, message, name=name)
        self.text = TextScroll(text)
        self.text.show()
        self.vbox.pack_start(self.text, TRUE, TRUE, 0)
        self.set_size_request(150, 300)
        

        
class _ScrollBox(Dialog):
    def __init__(self, message, name='MyScrollBox', type='v'):
        Dialog.__init__(self, message, name=name)
        self.scroll = ScrolledWindow()
        self.scroll.show()
        self.vbox.pack_start(self.scroll, TRUE, TRUE, 0)
        self.set_size_request(150, 300)
        if type =='v':
            self.mbox = VBox()
        else:
            self.mbox = HBox()
        self.scroll.add_with_viewport(self.mbox)
        self.mbox.show()
        
class ScrollVBox(_ScrollBox):
    def __init__(self, message, name='MyScrollBox'):
        _ScrollBox.__init__(self, message, name=name,
                            type='v')

class ScrollHBox(_ScrollBox):
    def __init__(self, message, name='MyScrollBox'):
        _ScrollBox.__init__(self, message, name=name,
                            type='h')

    
