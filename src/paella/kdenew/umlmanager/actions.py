from qt import QString
from kdecore import KShortcut
from kdeui import KGuiItem, KAction

from useless.kdebase.actions import BaseItem

# This class should go into useless
class BaseAction(KAction):
    def __init__(self, item, name, slot, parent):
        cut = KShortcut()
        KAction.__init__(self, item, cut, slot, parent, name)

class BootstrapItem(BaseItem):
    def __init__(self):
        BaseItem.__init__(self, 'Bootstrap System', 'boot',
                          'Bootstrap System', 'Bootstrap System')

class BootstrapMachine(BaseAction):
    def __init__(self, slot, parent):
        BaseAction.__init__(self, BootstrapItem(),
                            'BootstrapMachine', slot, parent)

class BackupMachineItem(BaseItem):
    def __init__(self):
        BaseItem.__init__(self, 'Backup machine', 'filesave',
                          'Backup machine into archive', 'Backup machine into archive')

class BackupMachine(BaseAction):
    def __init__(self, slot, parent):
        BaseAction.__init__(self, BackupMachineItem(),
                            'BackupMachine', slot, parent)

class InstallMachineItem(BaseItem):
    def __init__(self):
        BaseItem.__init__(self, 'Install machine', 'install',
                          'Install a machine', 'Install a machine')

class InstallMachine(BaseAction):
    def __init__(self, slot, parent):
        BaseAction.__init__(self, InstallMachineItem(),
                            'InstallMachine', slot, parent)
        
class RestoreMachineItem(BaseItem):
    def __init__(self):
        BaseItem.__init__(self, 'Restore machine', 'redo',
                          'Restore a machine from previous backup',
                          'Restore a machine from previous backup')

class RestoreMachine(BaseAction):
    def __init__(self, slot, parent):
        BaseAction.__init__(self, RestoreMachineItem(),
                            'RestoreMachine', slot, parent)

class LaunchMachineItem(BaseItem):
    def __init__(self):
        BaseItem.__init__(self, 'Launch machine', 'launch',
                          'Launch a machine', 'Launch a machine')

class LaunchMachine(BaseAction):
    def __init__(self, slot, parent):
        BaseAction.__init__(self, LaunchMachineItem(),
                            'LaunchMachine', slot, parent)
        
class EditConfigFileItem(BaseItem):
    def __init__(self):
        BaseItem.__init__(self, 'Edit .umlmachines.conf file',
                          'edit', 'Edit the main configuration',
                          'Edit the main configuration')

class EditConfigFile(BaseAction):
    def __init__(self, slot, parent):
        BaseAction.__init__(self, EditConfigFileItem(),
                            'EditConfigFile', slot, parent)
        
