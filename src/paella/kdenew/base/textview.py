from qtext import QextScintilla
from qtext import QextScintillaLexer
from qtext import QextScintillaLexerPython

# I need to locate the documentation for this
class HighlightTextView(QextScintilla):
    def __init__(self, parent, name='HighlightTextView'):
        QextScintilla.__init__(self, parent, name)
        self.pylex = QextScintillaLexerPython(self)
        self.lex = QextScintillaLexer(self)

    def setText(self, text):
        # ugly hack to highlight python code
        # grab the first line
        line = text.split('\n')[0]
        if 'python' in line:
            self.setLexer(self.pylex)
        else:
            self.setLexer(self.lex)
        QextScintilla.setText(self, text)
        
