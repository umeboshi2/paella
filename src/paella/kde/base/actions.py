from qt import QString
from kdecore import KShortcut
from kdeui import KGuiItem, KAction


class BaseItem(KGuiItem):
    def __init__(self, text, icon, ttip, whatsit):
        KGuiItem.__init__(self, QString(text), QString(icon), QString(ttip),
                          QString(whatsit))
        
class EditAddressesItem(KGuiItem):
    def __init__(self):
        text = QString('Edit addresses')
        icon = QString('edit')
        ttip = QString('Edit addresses')
        wtf = QString('edit or browse addresses')
        KGuiItem.__init__(self, text, icon, ttip, wtf)

class EditAddresses(KAction):
    def __init__(self, slot, parent):
        item = EditAddressesItem()
        name = 'EditAddresses'
        cut = KShortcut()
        KAction.__init__(self, item, cut, slot, parent, name)

class ManageClientsItem(KGuiItem):
    def __init__(self):
        text = QString('Manage Clients')
        icon = QString('identity')
        ttip = QString('Manage Clients')
        wtf = QString('manage or browse Clients')
        KGuiItem.__init__(self, text, icon, ttip, wtf)

class ManageClients(KAction):
    def __init__(self, slot, parent):
        item = ManageClientsItem()
        name = 'ManageClients'
        cut = KShortcut()
        KAction.__init__(self, item, cut, slot, parent, name)

    
class ManageTicketsItem(BaseItem):
    def __init__(self):
        BaseItem.__init__(self, 'Manage Tickets', 'contents',
                          'Manage Tickets', 'manage or brouse Tickets')

class ManageTickets(KAction):
    def __init__(self, slot, parent):
        item = ManageTicketsItem()
        name = 'ManageTickets'
        cut = KShortcut()
        KAction.__init__(self, item, cut, slot, parent, name)

class ManageTasksItem(BaseItem):
    def __init__(self):
        BaseItem.__init__(self, 'Manage Tasks', 'attach',
                          'Manage Tasks', 'manage or brouse Tasks')

class ManageTasks(KAction):
    def __init__(self, slot, parent):
        item = ManageTasksItem()
        name = 'ManageTasks'
        cut = KShortcut()
        KAction.__init__(self, item, cut, slot, parent, name)


class ConfigItem(BaseItem):
    def __init__(self):
        BaseItem.__init__(self, 'Configure Konsultant', 'configure',
                          'Configure Konsultant', 'Configure Konsultant')
        
class ConfigureKonsultant(KAction):
    def __init__(self, slot, parent):
        item = ConfigItem()
        name = 'ConfigureKonsultant'
        cut = KShortcut()
        KAction.__init__(self, item, cut, slot, parent, name)

class AdministerDatabaseItem(BaseItem):
    def __init__(self):
        BaseItem.__init__(self, 'Administer Database', 'tool_expert',
                          'Administer Database', 'administers database')

class AdministerDatabase(KAction):
    def __init__(self, slot, parent):
        item = AdministerDatabaseItem()
        name = 'AdministerDatabase'
        cut = KShortcut()
        KAction.__init__(self,  item, cut, slot, parent, name)
        
class AddDbUserItem(BaseItem):
    def __init__(self):
        BaseItem.__init__(self, 'Add User', 'filenew',
                          'Add Database User', 'adds a user to the database server')
        
class AddDbUser(KAction):
    def __init__(self, slot, parent):
        item = AddDbUserItem()
        name = 'AddDbUser'
        cut = KShortcut()
        KAction.__init__(self, item, cut, slot, parent, name)
    
class AddDbGroupItem(BaseItem):
    def __init__(self):
        BaseItem.__init__(self, 'Add Group', 'folder_new',
                          'Add Database Group', 'adds a group to the database server')
        
class AddDbGroup(KAction):
    def __init__(self, slot, parent):
        item = AddDbGroupItem()
        name = 'AddDbGroup'
        cut = KShortcut()
        KAction.__init__(self, item, cut, slot, parent, name)
    
class AddDbSchemaItem(BaseItem):
    def __init__(self):
        BaseItem.__init__(self, 'Add Schema', 'appearance',
                          'Add Database Schema', 'adds a new schema to the database')

class AddDbSchema(KAction):
    def __init__(self, slot, parent):
        item = AddDbSchemaItem()
        name = 'AddDbSchema'
        cut = KShortcut()
        KAction.__init__(self, item, cut, slot, parent, name)
        
