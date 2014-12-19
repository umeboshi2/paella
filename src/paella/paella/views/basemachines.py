import os
import json
import logging

from pyramid.exceptions import HTTPNotFound
from pyramid.exceptions import HTTPBadRequest
from pyramid.exceptions import HTTPForbidden


from cornice.resource import resource, view


from paella.managers.machines import MachineManager
from paella.managers.recipes import PartmanRecipeManager
from paella.managers.recipes import PartmanRaidRecipeManager
from paella.managers.pxeconfig import make_pxeconfig, remove_pxeconfig
from paella.managers.pxeconfig import pxeconfig_filename

log = logging.getLogger(__name__)


# Machine POST Actions
#
# submit - submit a brand new machien
#
# install - sets a machine to be installed
#
# stage_over - tells paella server that debian-installer has completed
#
# 

class BaseMachineResource(object):
    def __init__(self, request):
        self.request = request
        self.db = self.request.db
        self.mgr = MachineManager(self.db)
        self.recipes = PartmanRecipeManager(self.db)
        self.raid_recipes = PartmanRaidRecipeManager(self.db)
        

    def collection_get(self):
        return dict(data=self.mgr.list_machines())

    def get(self):
        uuid = self.request.matchdict['uuid']
        machine = self.mgr.get_by_uuid(uuid)
        return machine.serialize()

    def has_pxeconfig(self, machine, filename=None):
        if filename is None:
            filename = pxeconfig_filename(machine.uuid)
        return os.path.isfile(filename)


    def _set_machine_install(self, machine, install=True):
        settings = self.request.registry.settings
        filename = pxeconfig_filename(machine.uuid)
        if install:
            make_pxeconfig(machine, settings)
            if not self.has_pxeconfig(machine, filename=filename):
                raise RuntimeError, "%s doesn't exist." % filename
        else:
            remove_pxeconfig(machine.uuid)
            if self.has_pxeconfig(machine, filename=filename):
                raise RuntimeError, "%s still exists." % filename
                
            
