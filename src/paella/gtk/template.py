import os
from os.path import join, dirname, isfile

from paella.base import Error, debug
from paella.base.defaults import DELIMITERS
from paella.base.template import Template
from paella.base.util import ujoin

from paella.gtk.simple import TextScroll
from paella.gtk.helpers import get_buffer_text, HasDialogs
from paella.gtk import dialogs

from gtk import MenuItem, FileSelection
from gtk import TRUE, FALSE, mainquit, mainloop

from gtk import TextBuffer, TextTag, TextView

class _TemplateTag(TextTag):
    def __init__(self, name, foreground='magenta', scale=.85):
        TextTag.__init__(self, name=name)
        self.set_property('name', name)
        self.set_property('foreground', foreground)
        self.set_property('scale', scale)
        


class TextTemplate(TextBuffer):
    def __init__(self, name='TextTemplate'):
        TextBuffer.__init__(self)
        #self.set_name(name)
        self.__tagtable__ = self.get_tag_table()
        template_tag = _TemplateTag('template', foreground='magenta', scale=.85)
        self.__tagtable__.add(template_tag)
        self.__template__ = Template()
        #StringTemplate('', delimiters=self.delimiters)
        

    def _remake_tag_(self, span):
        start, end = span
        tagtext = self.__template__.template[start:end]
        start, end = map(self.get_iter_at_offset, span)
        self.delete(start, end)
        self.insert_with_tags_by_name(start, tagtext, 'template')

    def position_tag(self):
        start, end = self.get_selection_bounds()
        self.__replace_pos__ = start, end

    def tag_slice(self):
        return self.get_slice(*self.__replace_pos__)

    def insert_tag(self, keytext):
        self.position_tag()
        start, end = self.__replace_pos__
        text = self.get_slice(start, end)
        self.delete(start, end)
        left, right = self.__template__.delimiters
        tag = ''.join([left, keytext, right])
        self.insert_with_tags_by_name(start, tag, 'template')
        self.__template__[keytext] = text
        self.reset_template()

    def set_text(self, text):
        TextBuffer.set_text(self, text)
        self.reset_template()

    def reset_template(self):
        text = get_buffer_text(self)
        self.__template__.set_template(text)
        map(self._remake_tag_, self.__template__.spans())
        
    def set_subs(self, datadict):
        self.__template__.clear()
        self.__template__.update(datadict)
        self.reset_template()

    def preview(self):
        return str(self.__template__.sub())

    def get_full_text(self):
        return self.get_text(*self.get_bounds())

class TemplateEditor(TextView, HasDialogs):
    def __init__(self, cfg=None, name='TemplateEditor'):
        TextView.__init__(self)
        self.cfg = cfg
        self.set_name(name)
        self.buffer = TextTemplate(name=name)
        self.set_buffer(self.buffer)
        self.dialogs = {}.fromkeys(['create', 'preview'])
        self.set_editable(True)
        self.show()
        
    def make_tag(self, tagname):
        self.buffer.position_tag()
        self.buffer.insert_tag(tagname)

    def create_new_tag(self, creator):
        self.buffer.position_tag()
        value = self.buffer.tag_slice()
        if self.dialogs['create'] is None:
            dialog = dialogs.RecordEntry('create variable named',
                                         {}.fromkeys(['name', 'value'], ''), 'create')
            self.dialogs['create'] = dialog
            dialog.set_ok(creator)
            dialog.set_cancel(self.destroy_dialog)
            dialog['value'] = self.buffer.tag_slice()

    def preview(self, *args):
        if self.dialogs['preview'] is None:
            dialog = dialogs.TextDialog('preview', self.buffer.preview())
            self.dialogs['preview'] = dialog
            #dialog.set_ok(self.destroy_dialog)
            dialog.set_cancel(self.destroy_dialog)
    
    def get_text(self):
        return self.buffer.get_full_text()

class Templatefopo:
    pass
                                         
        

if __name__ == '__main__':
    pass
