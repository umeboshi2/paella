from string import strip
import os, os.path


from paella.base.config import Configuration
from paella.gtk.dialogs import CList, Entry
from paella.gtk.middle import ScrollCList
from paella.gtk.middle import ListNoteBook, ItemButtonBox
from paella.gtk.windows import CommandBoxWindow
from gtk import mainloop, mainquit

from paella.db.lowlevel import QuickConn
from paella.db.midlevel import StatementCursor
from paella.sqlgen.defaults import NameTable
from paella.sqlgen.write import insert, update


from gtk import DEST_DEFAULT_MOTION
from gtk import DEST_DEFAULT_HIGHLIGHT
from gtk import DEST_DEFAULT_DROP
from gtk.gdk import ACTION_COPY, ACTION_MOVE
from gtk.gdk import BUTTON1_MASK
from gtk import STATE_NORMAL, STATE_PRELIGHT
from gtk.gdk import Color as GdkColor

config = Configuration()
template_path = os.path.expanduser(config['template_path'])
template_path = os.path.join(template_path, 'themes')
style_elements = ['fg', 'bg', 'base', 'text']
element_states = ['ACTIVE', 'INSENSITIVE',
                  'NORMAL', 'PRELIGHT', 'SELECTED']

gtk1rcpath = 'gtk/gtkrc'
gtk2rcpath = 'gtk-2.0/gtkrc'

theme_base = 'ice-base'

color_target = ('color', 0, 22)

def _bg_widget(widget, color):
    widget.modify_bg(STATE_NORMAL, GdkColor(*map(lambda x:256*x, color.triple)))
class ThemeTable(NameTable):
    def __init__(self, name):
        columns = ['element'] + element_states
        NameTable.__init__(self, name, columns)

def _setup_db(cursor):
    table = NameTable('themes', ['theme'])
    cursor.create_table(table)
    cursor.insert(table='themes', data={'theme':'themebase'})
    table = ThemeTable('themebase')
    cursor.create_table(table)
    cols = [x.name for x in t.columns]
    #print cursor.tables()
    cursor.set_table(table.name)
    cursor.insert(data=dict(zip(cols, ['fg', 'black', 'seashell', 'black', 'sky blue', 'plum'])))
    cursor.insert(data=dict(zip(cols, ['bg', 'cyan3', 'seashell',
                    'cyan4', 'light coral', 'grey'])))
    cursor.insert(data=dict(zip(cols, ['base', 'light sea green',
                    'lavender', 'azure3', 'yellow', 'aquamarine'])))
    cursor.insert(data=dict(zip(cols, ['text', 'wheat', 'black',
                    'black', 'black', 'dark violet'])))

def _theme_path(name, version=None):
    base = os.path.expanduser(os.path.join('~', '.themes', name))
    if version == 1:
        return os.path.join(base, os.path.dirname(gtk1rcpath))
    elif version == 2:
        return os.path.join(base, os.path.dirname(gtk2rcpath))
    else:
        return base


def make_theme_dirs(name):
    p1 = _theme_path(name, version=1)
    p2 = _theme_path(name, version=2)
    for p in [p1, p2]:
        if not os.path.isdir(p):
            os.makedirs(p)
            
    
class Color(object):
    def __init__(self, name, triple):
        object.__init__(self)
        self.name = name
        self.triple = triple
        self.version = 2
        self.plain = 0
        
    def as_hex(self):
        return '%02x%02x%02x' %tuple(self.triple)
    def set_version(self, version):
        self.version = version
    def set_plain(self, plain):
        self.plain = plain
        
    def __write__(self):
        if self.version == 2:
            return '%s' % self.name
        else:
            return '#%s' % self.as_hex()

    def __repr__(self):
        if self.plain:
            return self.__write__()
        else:
            return '"%s"' %self.__write__()

class Rgbdb(object):
    def __init__(self, path='/etc/X11/rgb.txt'):
        object.__init__(self)
        rgbfile = file(path)
        self.colordict = {}
        for line in rgbfile:
            if line[0] != '!':
                triple, name = map(strip, line.split('\t\t'))
                self.colordict[name] = Color(name, map(int, triple.split()))
        rgbfile.close()
        
    def __getitem__(self, name):
        color = self.colordict[name]
        return Color(color.name, color.triple)

    def items(self):
        return self.colordict.items()
    def values(self):
        return self.colordict.values()
    def keys(self):
        return self.colordict.values()
    def set_plain(self, plain):
        for color in self.colordict.values():
            color.set_plain(plain)
            

class Element(object):
    def __init__(self, rgb, name, items=[], states=element_states):
        object.__init__(self)
        self.rgb = rgb
        self.name = name
        self.states = states
        self.quick_set(items)
        
    def _set_dict_(self):
        self._sdict = dict(self._state_items_)

    def __getitem__(self, state):
        return self._sdict[state]
    def __setitem__(self, state, color):
        index = self.states.index(state)
        if type(color) == str:
            color = Color(color, self.rgb[color].triple)
        self._state_items_[index] = (state, color)
        self._set_dict_()
    def items(self):
        return self._state_items_
    def values(self):
        return [v for k,v in self._state_items_]
    def keys(self):
        return self.states
    def quick_set(self, items):
        if len(items):
            items = [self.rgb[x] for x in items]
            idict = dict(zip(self.states, items))
            self._state_items_ = [(s,idict[s]) for s in self.states]
        else:
            self._state_items_ = []
            for state in self.states:
                self._state_items_.append((state, Color('black', self.rgb['black'])))
        self._set_dict_()
        
            
        
        
class Style(object):
    def __init__(self, rgb):
        object.__init__(self)
        self.rgb = rgb
        self._elements = style_elements
        self._element_items_ = []
        for e in self._elements:
            self._element_items_.append(Element(self.rgb, e))
        self.version = 2
        self.elements = dict(zip(self._elements, self._element_items_))
        
    def __getitem__(self, key):
        key1, key2 = key.split('_')
        return self.elements[key1][key2]
    def __setitem__(self, key, value):
        key1, key2 = key.split('_')
        self.elements[key1][key2] = Color(value, self.rgb[value].triple)

    def set_version(self, version):
        #self.version = version
        for color in self.to_dict().values():
            color.set_version(version)

    def keys(self):
        keylist = []
        for k1,v in self.elements.items():
            for k2 in v.keys():
                keylist.append('_'.join([k1,k2]))
        return keylist

    def to_dict(self):
        keys = self.keys()
        values = [self[key] for key in keys]
        return dict(zip(keys, values))
    def to_tmpldict(self):
        keys = self.keys()
        values = [self[key] for key in keys]
        for v in values:
            v.plain = 0
        return dict(zip(keys, values))

    def to_irows(self):
        rows = []
        for element, states in self.elements.items():
            etuple = [('element', element)]
            etuple += [(k,str(v.name)) for k,v in states.items()]
            idict = dict(etuple)
            rows.append(idict)
        return rows

    def to_urows(self):
        rows = []
        for element, states in self.elements.items():
            etuple = [('element', element)]
            etuple = [(k,str(v.name)) for k,v in states.items()]
            idict = dict(etuple)
            rows.append((element, idict))
        return rows
    
    def quick_set(self, rows):
        for row in rows:
            self.elements[row[0]].quick_set(row[1:])


class GtkrcTemplate(StringTemplate):
    def __init__(self, name, theme_base, style, version=2):
        self.delimiters = ['|=-', '-=|']
        self.name = name
        self.style = style
        self.version = version
        self.__set_tmplate_path__()
        template_file = file(self.template_path)
        template = template_file.read()
        template_file.close()
        StringTemplate.__init__(self, template, substitutions=self.style.to_tmpldict(),
                                delimiters = self.delimiters)
    

    def __set_tmplate_path__(self):
        if self.version == 1:
            rcpath = gtk1rcpath
        else:
            rcpath = gtk2rcpath
        self.template_path = os.path.join(template_path, theme_base, rcpath)
        
    def set_version(self, version):
        self.style.set_version(version)
        self.version = version
        self.__set_tmplate_path__()
        template_file = file(self.template_path)
        template = template_file.read()
        template_file.close()
        self.set_template(template)

    def write_files(self):
        make_theme_dirs(self.name)
        file1 = os.path.join(_theme_path(self.name), gtk1rcpath)
        file2 = os.path.join(_theme_path(self.name), gtk2rcpath)
        self.set_version(1)
        self.write(file1)
        self.set_version(2)
        self.write(file2)


class ColorThingy(ListNoteBook):
    def __init__(self, rgb):
        ListNoteBook.__init__(self)
        self.rgb = rgb
        self.rgb.set_plain(1)
        self._style = Style(self.rgb)
        self.set_rows(rgb.keys(), ['color'])
        self._elements = {}
        for element in style_elements:
            #color_names = [c.name for c in self._style.elements[element]
            name_dict = dict([(k,v.name) for k,v in self._style.elements[element].items()])
            container = ItemButtonBox(name_dict, name=element)
            self.append_page(container, element)
            self._elements[element] = container
            for button in container.vdict.values():
                button.connect('drag_data_received', self.drop_color)
                button.drag_dest_set(DEST_DEFAULT_MOTION |
                                        DEST_DEFAULT_HIGHLIGHT |
                                        DEST_DEFAULT_DROP,
                                        [color_target], ACTION_COPY)
        self.listbox.connect('drag_data_get', self.drag_color)
        self.listbox.drag_source_set(BUTTON1_MASK, [color_target],
                                     ACTION_COPY)

    def __set_button__(self, element, state, color):
        self._elements[element][upper(state)] = color

    def drop_color(self, *args):
        ibutton, context, x, y, selection, targettype, time = args
        print 'dropped'
        color = selection.data
        triple = self.rgb[color].triple
        print color, triple, 'debug'

        #print dir(ibutton.button)
        ibutton.button.set_label(color)
        _bg_widget(ibutton.button, self.rgb[color])
        ibutton.button.modify_bg(STATE_NORMAL,
                                 GdkColor(*map(lambda x:256*x, triple)))
        print ibutton.get_name()
        self._style[ibutton.get_name()] = color
        self._style[ibutton.get_name()].plain = 1
    def drag_color(self, *args):
        lbox, context, selection, targettype, time = args
        print 'its a drag'
        print selection.data
        selection.set(selection.target, 0, lbox.get_selected_data()[0][0].name)

class ColorThingyWindow(CommandBoxWindow):
    def __init__(self, rgb, conn, name='ColorThingyWindow'):
        CommandBoxWindow.__init__(self, name=name)
        self.browser = ColorThingy(rgb)
        self.rgb = rgb
        self.cmd = StatementCursor(conn, 'themer')
        self.theme = None
        self.vbox.add(self.browser)
        self.tbar.add_button('import', 'import', self.__ask_import__)
        self.tbar.add_button('insert', 'insert', self.__ask_insert__)
        self.tbar.add_button('update', 'update', self.__update_theme__)
        self.tbar.add_button('save', 'save', self.__save_files__)
        self._insert_box = None
        self._import_box = None

    def __ask_import__(self, *args):
        if not self._import_box:
            #print args
            #print '__import__'
            themes = self.cmd.getall(['theme'], 'themes')
            self._import_box = CList('hello')
            self._import_box.set_rows(themes)
            self._import_box.set_ok(self.__import_ok__)

    def __import_ok__(self, *args):
        theme = self._import_box.listbox.get_selected_data()[0]['theme']
        self._import_box.destroy()
        self._import_box = None
        rows = self.cmd.select(table=theme)
        b = self.browser
        b._style.quick_set(rows)
        for e, sb in b._elements.items():
            for s in sb.keys():
                color = b._style.elements[e][s]        
                sb[s] = color.name
                _bg_widget(sb[s].button, color)
        self.theme = theme
                                     
    def __ask_insert__(self, *args):
        if not self._import_box:
            self._insert_box = EntryDialog('please insert name')
            self._insert_box.set_ok(self.__insert_ok__)

    def __insert_ok__(self, *args):
        style = self.browser._style
        tname = self._insert_box.get()
        self.theme = tname
        table = ThemeTable(tname)
        self.cmd.create_table(table)
        self.cmd.insert('themes', {'theme':tname})
        for row in style.to_irows():
            self.cmd.insert(tname, row)

    def __update_theme__(self, *args):
        if self.theme:
            for element, states in self.browser._style.to_urows():
                self.cmd.update(self.theme, states, "element = '%s'" %element)
    def __save_files__(self, *args):
        colordict = Rgbdb()
        tmpl = GtkrcTemplate(self.theme, theme_base, self.browser._style)
        tmpl.write_files()
        
        
        
        
if __name__ == '__main__':
    cd = Rgbdb()
    tp = os.path.expanduser(g['template_path'])
    fg, bg, base, text = {}, {}, {}, {}
    s = Style(cd)#fg, bg, base, text)
    tmpl = GtkrcTemplate('test', theme_base, s)
    cd.set_plain(1)
    c = QuickConn()
    win = ColorThingyWindow(cd, c)
    t = NameTable('themes', ['theme'])
    cmd = CommandCursor(c, 'dsfsdf')
    def dtable():
        cmd.execute('drop table themebase')
    def dtables():
        for t in cmd.tables():
            if t not in  ['footable']:
                cmd.execute('drop table %s' %t)
    #dtables()
    mainloop()
    
