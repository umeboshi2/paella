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
        BaseItem.__init__(self, 'Manage Families', 'personal',
                          'Manage Families', 'Manage Families')
        
class ManageFamilies(BaseAction):
    def __init__(self, slot, parent):
        BaseAction.__init__(self, ManageFamiliesItem(),
                            'ManageFamilies', slot, parent)
        
class DiffItemOrig(BaseItem):
    def __init__(self):
        BaseItem.__init__(self, 'Diff', 'view_left_right',
                          'Diff', 'Diff')

class DiffItem(BaseItem):
    def __init__(self):
        BaseItem.__init__(self, 'Diff', 'kdmconfig',
                          'Diff', 'Diff')

class DiffAction(BaseAction):
    def __init__(self, slot, parent):
        BaseAction.__init__(self, DiffItem(), 'Diff', slot, parent)
        
class EditItem(BaseItem):
    def __init__(self):
        BaseItem.__init__(self, 'edit', 'edit',
                          'edit', 'edit')

class EditAction(BaseAction):
    def __init__(self, slot, parent):
        BaseAction.__init__(self, EditItem(), 'Edit', slot, parent)

class EditTemplateItem(BaseItem):
    def __init__(self):
        BaseItem.__init__(self, 'Edit Templates', 'colors',
                          'edit templates', 'edit templates')

class EditTemplateAction(BaseAction):
    def __init__(self, slot, parent):
        BaseAction.__init__(self, EditTemplateItem(), 'EditTemplates', slot, parent)
        
class OpenSystemTarballItem(BaseItem):
    def __init__(self):
        BaseItem.__init__(self, 'systarball', 'fileopen',
                          'open system tarball', 'open system tarball')

class OpenSystemTarballAction(BaseAction):
    def __init__(self, slot, parent):
        BaseAction.__init__(self, OpenSystemTarballItem(),
                            'OpenSystemTarball', slot, parent)

class SaveTemplateToTraitItem(BaseItem):
    def __init__(self):
        BaseItem.__init__(self, 'save template', 'filesave',
                          'save template to trait', 'save template to trait')

class SaveTemplateToTraitAction(BaseAction):
    def __init__(self, slot, parent):
        BaseAction.__init__(self, SaveTemplateToTraitItem(), 'SaveTemplateToTrait', slot, parent)
        
class ChangeSuiteItem(BaseItem):
    def __init__(self):
        BaseItem.__init__(self, 'change suite', 'colors',
                          'change suite', 'change suite')

class ChangeSuiteAction(BaseAction):
    def __init__(self, slot, parent):
        BaseAction.__init__(self, ChangeSuiteItem(), 'ChangeSuite', slot, parent)
