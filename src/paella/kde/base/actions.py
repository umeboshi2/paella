from qt import QString
from kdecore import KShortcut
from kdeui import KGuiItem, KAction

from kommon.base.actions import BaseItem
class BaseAction(KAction):
    def __init__(self, item, name, slot, parent):
        cut = KShortcut()
        KAction.__init__(self, item, cut, slot, parent, name)
        
class ManageFamiliesItem(BaseItem):
    def __init__(self):
        BaseItem.__init__(self, 'Manage Families', 'gv',
                          'Manage Families', 'Manage Families')
        
class ManageFamilies(BaseAction):
    def __init__(self, slot, parent):
        BaseAction.__init__(self, ManageFamiliesItem(),
                            'ManageFamilies', slot, parent)
        
class DiffItem(BaseItem):
    def __init__(self):
        BaseItem.__init__(self, 'Diff', 'view_left_right',
                          'Diff', 'Diff')

class DiffAction(BaseAction):
    def __init__(self, slot, parent):
        BaseAction.__init__(self, DiffItem(), 'Diff', slot, parent)
        
