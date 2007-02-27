from qt import QSyntaxHighlighter
from qt import QColor

from kdeui import KTextEdit

from useless.base.template import Template
from useless.kdebase import get_application_pointer
from paella.kdenew.base.mainwin import BasePaellaWindow

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

class TemplateViewWindow(BasePaellaWindow):
    def __init__(self, parent, name='TemplateViewWindow'):
        BasePaellaWindow.__init__(self, parent, name=name)
        self.initPaellaCommon()
        self.mainView = TemplateTextEdit(self)
        self.setCentralWidget(self.mainView)
        
