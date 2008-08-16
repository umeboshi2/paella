from qt import QString
from kdecore import KShortcut
from kdeui import KGuiItem, KAction

from useless.kdebase.actions import BaseItem

# This class should go into useless
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

class ImportDatabaseItem(BaseItem):
    def __init__(self):
        tt = 'Import the database from a previous xml export.'
        BaseItem.__init__(self, 'Import database', 'restore', tt, tt)

class ImportDatabaseAction(BaseAction):
    def __init__(self, slot, parent):
        BaseAction.__init__(self, ImportDatabaseItem(), 'ImportDatabaseAction',
                            slot, parent)

class ExportDatabaseItem(BaseItem):
    def __init__(self):
        tt = 'Export the database to xml.'
        BaseItem.__init__(self, 'Export database', 'export', tt, tt)

class ExportDatabaseAction(BaseAction):
    def __init__(self, slot, parent):
        BaseAction.__init__(self, ExportDatabaseItem(), 'ExportDatabaseAction',
                            slot, parent)
        
class ConnectDatabaseItem(BaseItem):
    def __init__(self):
        tt = 'Connect to a database'
        BaseItem.__init__(self, 'Connect to database', 'connect_creating', tt, tt)
        
class ConnectDatabaseAction(BaseAction):
    def __init__(self, slot, parent):
        BaseAction.__init__(self, ConnectDatabaseItem(), 'ConnectDatabaseAction',
                            slot, parent)
        
class DisconnectDatabaseItem(BaseItem):
    def __init__(self):
        tt = 'Disconnect from a database'
        BaseItem.__init__(self, 'Disconnect from database', 'connect_no', tt, tt)
        
class DisconnectDatabaseAction(BaseAction):
    def __init__(self, slot, parent):
        BaseAction.__init__(self, DisconnectDatabaseItem(), 'DisconnectDatabaseAction',
                            slot, parent)

class OpenSuiteManagerItem(BaseItem):
    def __init__(self):
        tt = 'Open SuiteManager'
        BaseItem.__init__(self, tt, 'colors', tt, tt)

class OpenSuiteManagerAction(BaseAction):
    def __init__(self, slot, parent):
        BaseAction.__init__(self, OpenSuiteManagerItem(), 'OpenSuiteManagerAction',
                            slot, parent)
    
dbactions = dict(export=ExportDatabaseAction,
                 connect=ConnectDatabaseAction, disconnect=DisconnectDatabaseAction)
dbactions['import'] = ImportDatabaseAction

class ManageAptSourcesItem(BaseItem):
    def __init__(self):
        tt = 'Manage Apt Sources'
        BaseItem.__init__(self, tt, 'player_playlist', tt, tt)

class ManageAptSourcesAction(BaseAction):
    def __init__(self, slot, parent):
        BaseAction.__init__(self, ManageAptSourcesItem(), 'ManageAptSourcesAction',
                            slot, parent)

class ManageAptKeysItem(BaseItem):
    def __init__(self):
        tt = 'Manage Apt Keys'
        BaseItem.__init__(self, tt, 'key', tt, tt)

class ManageAptKeysAction(BaseAction):
    def __init__(self, slot, parent):
        BaseAction.__init__(self, ManageAptKeysItem(), 'ManageAptKeysAction',
                            slot, parent)
        
