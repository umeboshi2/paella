from string import strip
import os, os.path

from HTMLgen import StringTemplate


from paella.classes.config import Configuration


from gtk import DEST_DEFAULT_MOTION
from gtk import DEST_DEFAULT_HIGHLIGHT
from gtk import DEST_DEFAULT_DROP
from gtk.gdk import ACTION_COPY, ACTION_MOVE
from gtk.gdk import BUTTON1_MASK
from gtk import STATE_NORMAL, STATE_PRELIGHT
from gtk.gdk import Color as GdkColor

config = Configuration()
template_path = os.path.expanduser(config['template_path'])

style_elements = ['fg', 'bg', 'base', 'text']
element_states = ['ACTIVE', 'INSENSITIVE',
                  'NORMAL', 'PRELIGHT', 'SELECTED']

gtk1rcpath = 'gtk/gtkrc'
gtk2rcpath = 'gtk-2.0/gtkrc'

def _bg_widget(widget, color):
    widget.modify_bg(STATE_NORMAL, GdkColor(*map(lambda x:256*x, color.triple)))

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
        self.theme_base = theme_base
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
        self.template_path = os.path.join(template_path, self.theme_base, rcpath)
        
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
        
        
        
if __name__ == '__main__':
    cd = Rgbdb()
    tp = os.path.expanduser(g['template_path'])
    s = Style(cd)
    tmpl = GtkrcTemplate('test', theme_base, s)
    cd.set_plain(1)

    
    
