from qt import QString
from kdecore import KShortcut
from kdeui import KGuiItem, KAction


class BaseItem(KGuiItem):
    def __init__(self, text, icon, ttip, whatsit):
        KGuiItem.__init__(self, QString(text), QString(icon), QString(ttip),
                          QString(whatsit))
        
