from qt import SIGNAL
from qt import QSyntaxHighlighter
from qt import QColor
from qt import QPopupMenu

from kdeui import KTextEdit
from kdeui import KMessageBox
from kdeui import KStdAction

from useless.base.util import strfile
from useless.base.template import Template
from useless.kdebase import get_application_pointer
from useless.kdebase.dialogs import BaseRecordDialog

from paella.db.trait.main import Trait

from paella.kde.base.mainwin import BasePaellaWindow
from paella.kde.base.dialogs import NewTraitVariableDialog

class TemplateHighlighter(QSyntaxHighlighter):
    def highlightParagraph(self, text, endStateOfLastPara):
        text = str(text)
        template = Template()
        template.set_template(text)
        for span in template.spans():
            font = self.textEdit().currentFont()
            font.setBold(True)
            color = QColor('blue')
            length = span[1] - span[0]
            self.setFormat(span[0], length, font, color)
        return 0


class TemplateTextEdit(KTextEdit):
    def __init__(self, parent, name='TemplateTextEdit'):
        KTextEdit.__init__(self, parent, name)
        self.app = get_application_pointer()
        self.hl = TemplateHighlighter(self)
        self.trait = parent.trait

    def createPopupMenu(self, pos=None):
        if pos is None:
            menu = KTextEdit.createPopupMenu(self)
        else:
            menu = KTextEdit.createPopupMenu(self, pos)
        ident = menu.insertItem('Hello There', self.slotHelloThere)
        if self.hasSelectedText():
            print self.selectedText()
            print self.getSelection()
        print 'ident', ident
        menu.setItemParameter(ident, 777)
        env = self.trait.get_full_environment()
        # make a magic number to start id's on variables
        varcount = 1234
        lookup = {}
        for trait, traitvars in env:
            tmenu = QPopupMenu(menu)
            menu.insertItem(trait, tmenu)
            keys = traitvars.keys()
            keys.sort()
            for key in keys:
                varcount += 1
                ident = tmenu.insertItem(key, self.slotHelloThere)
                tmenu.setItemParameter(ident, varcount)
                lookup[varcount] = (trait, key)
        self.lookup = lookup
        menu.insertItem('Create New Variable', self.slotCreateNewVariable)
        return menu

    def slotHelloThere(self, arg=None):
        trait, name = self.lookup[arg]
        self.tag_selection(trait, name)

    def slotCreateNewVariable(self, arg=None):
        print arg
        text = ''
        if self.hasSelectedText():
            text = str(self.selectedText())
        win = NewTraitVariableDialog(self)
        if text:
            win.setRecordData(dict(value=text))
        win.connect(win, SIGNAL('okClicked()'),
                    self.slotCreateNewVariableSelected)
        win.show()
        self._dialog = win

    def tag_selection(self, trait, name):
        if not self.hasSelectedText():
            raise RuntimeError, 'we need selected text'
        template = Template()
        left, right = template.delimiters
        tagname = '_'.join([trait, name])
        tag = ''.join([left, tagname, right])
        pstart, istart, pend, iend = self.getSelection()
        self.removeSelectedText()
        self.insertAt(tag, pstart, istart)
        
        
    def slotCreateNewVariableSelected(self):
        win = self._dialog
        data = win.getRecordData()
        name = data['name']
        value = data['value']
        print name, value
        self.trait.environ[name] = value
        print self.trait.environ
        self._dialog = None
        self.tag_selection(self.trait.current_trait, name)
        
        
        
            
class TemplateViewWindow(BasePaellaWindow):
    def __init__(self, parent, suite, trait, template, name='TemplateViewWindow'):
        BasePaellaWindow.__init__(self, parent, name=name)
        self.initPaellaCommon()
        self.trait = Trait(self.conn, suite=suite)
        self.trait.set_trait(trait)
        self.mainView = TemplateTextEdit(self)
        self.connect(self.mainView, SIGNAL('textChanged()'), self.slotTextChanged)
        self.statusBar()
        self.setCentralWidget(self.mainView)
        self.resize(600, 800)
        self.initActions()
        self.initMenus()
        self.initToolbar()
        self.set_template(template)
        

    def set_template(self, template):
        self.current_template = template
        self._set_template()

    def _status_msg(self, status=None):
        msg = 'Trait: %s' % self.trait.current_trait
        msg = '%s (template %s)' % (msg, self.current_template)
        if status is None:
            return msg
        else:
            return '%s %s' % (status, msg)

    def _update_status(self, status=None):
        msg = self._status_msg(status=status)
        self.statusBar().message(msg)
        
    def _set_template(self):
        template = self.current_template
        data = self.trait.get_template_contents(template)
        self.mainView.setText(data)
        self._update_status()
    
    def initActions(self):
        collection = self.actionCollection()
        self.quitAction = KStdAction.quit(self.close, collection)
        self.saveAction = KStdAction.save(self.slotSave, collection)
        self.newAction = KStdAction.openNew(self.mainView.slotCreateNewVariable, collection)
        
    def initMenus(self):
        pass
    
    def initToolbar(self):
        toolbar = self.toolBar()
        self.newAction.plug(toolbar)
        self.saveAction.plug(toolbar)
        self.quitAction.plug(toolbar)

    def slotTextChanged(self):
        self._update_status('CHANGED')
        
    def slotSave(self):
        data = dict(template=self.current_template)
        text = str(self.mainView.text())
        oldtext = self.trait.get_template_contents(self.current_template)
        if oldtext != text:
            templatefile = strfile(text)
            self.trait.update_template(data, templatefile)
            self._update_status('Saved')
        else:
            KMessageBox.information(self, 'Nothing has changed')
            self._update_status()
        

    

