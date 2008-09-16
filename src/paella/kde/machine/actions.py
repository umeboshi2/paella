from qt import QString
from kdecore import KShortcut
from kdeui import KGuiItem, KAction

from useless.kdebase.actions import BaseItem
from paella.kde.base.actions import BaseAction
        
class ManageMachinesItem(BaseItem):
    def __init__(self):
        BaseItem.__init__(self, 'manage machines', 'gohome',
                          'manage machines', 'manage machines')

class ManageMachinesAction(BaseAction):
    def __init__(self, slot, parent):
        BaseAction.__init__(self, ManageMachinesItem(), 'ManageMachines', slot, parent)

class ManageMachineTypesItem(BaseItem):
    def __init__(self):
        comment = 'manage machine types'
        BaseItem.__init__(self, comment, 'openterm', comment, comment)

class ManageMachineTypesAction(BaseAction):
    def __init__(self, slot, parent):
        BaseAction.__init__(self, ManageMachineTypesItem(), 'ManageMachineTypes',
                            slot, parent)

class ManageFilesystemsItem(BaseItem):
    def __init__(self):
        comment = 'manage filesystems'
        BaseItem.__init__(self, comment, 'blockdevice', comment, comment)

class ManageFilesystemsAction(BaseAction):
    def __init__(self, slot, parent):
        BaseAction.__init__(self, ManageFilesystemsItem(), 'ManageFilesystems',
                            slot, parent)

class ManageDisksItem(BaseItem):
    def __init__(self):
        comment = 'manage disks'
        BaseItem.__init__(self, comment, 'filesave', comment, comment)

class ManageDisksAction(BaseAction):
    def __init__(self, slot, parent):
        BaseAction.__init__(self, ManageDisksItem(), 'ManageDisks',
                            slot, parent)

class ManageDiskConfigItem(BaseItem):
    def __init__(self):
        comment = 'manage diskconfig'
        BaseItem.__init__(self, comment, 'blockdevice', comment, comment)

class ManageDiskConfigAction(BaseAction):
    def __init__(self, slot, parent):
        BaseAction.__init__(self, ManageDiskConfigItem(), 'ManageDiskConfig',
                            slot, parent)
        
class ManageMountsItem(BaseItem):
    def __init__(self):
        comment = 'manage mounts'
        BaseItem.__init__(self, comment, 'folder', comment, comment)

class ManageMountsAction(BaseAction):
    def __init__(self, slot, parent):
        BaseAction.__init__(self, ManageMountsItem(), 'ManageMounts',
                            slot, parent)

class ManageKernelsItem(BaseItem):
    def __init__(self):
        comment = 'manage kernels'
        BaseItem.__init__(self, comment, 'memory', comment, comment)

class ManageKernelsAction(BaseAction):
    def __init__(self, slot, parent):
        BaseAction.__init__(self, ManageKernelsItem(), 'ManageKernels',
                            slot, parent)

        
ManageActions = {
    'machine' : ManageMachinesAction,
    'machine_type' : ManageMachineTypesAction,
    'filesystem' : ManageFilesystemsAction,
    'disk' : ManageDisksAction,
    'mount' : ManageMountsAction,
    'diskconfig' : ManageDiskConfigAction,
    'kernels' : ManageKernelsAction
    }

ManageActionsOrder = ['machine', 'machine_type', 'diskconfig',
                      'kernels']
