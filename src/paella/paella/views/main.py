import os
import json

from pyramid.exceptions import HTTPNotFound
from pyramid.exceptions import HTTPBadRequest

from cornice.resource import resource, view


from paella.managers.main import MachineAddressManager
from paella.managers.pxeconfig import make_pxeconfig, remove_pxeconfig
from paella.managers.pxeconfig import pxeconfig_filename


from paella.views.base import BaseResource

@resource(collection_path='/api0/machines',
          path='/api0/machines/{name}')
class MachineResource(object):
    def __init__(self, request):
        self.request = request
        self.db = self.request.db
        self.mgr = MachineAddressManager(self.db)
        
    def collection_get(self):
        if self.request.GET.items():
            if 'uuid' not in self.request.GET:
                raise HTTPBadRequest
            uuid = self.request.GET['uuid']
            name = self.identify_machine_by_uuid(uuid)
            if name is None:
                raise HTTPNotFound, "No machine found with %s" % name
            return dict(name=name)
        else:
            return dict(data='need a list of machines')
        

    def _submit_machine(self, data):
        name = data['machine']
        addresses = data['addresses']
        uuid = None
        if 'uuid' in data:
            uuid = data['uuid']
        # add machine
        data = self.mgr.update_machine(name, addresses, uuid=uuid)
        # FIXME
        if data is not None:
            data['machine'] = data['machine'].serialize()
            data['addresses'] = [a.serialize() for a in data['addresses']]
        return data

    def _install_machine(self, data):
        name = data['machine']
        machine = self.mgr.get_machine(name)
        if machine.uuid:
            uuid = machine.uuid
            make_pxeconfig(uuid, name)
            filename = pxeconfig_filename(uuid)
            if not os.path.isfile(filename):
                raise RuntimeError, "%s doesn't exist." % filename
            return
        
        addresses = self.mgr.list_machine_addresses(name)
        for address in addresses:
            make_pxeconfig(address, name)
            filename = pxeconfig_filename(address)
            print "FILENAME: %s" % filename
            if not os.path.isfile(filename):
                raise RuntimeError, "%s doesn't exist." % filename
            
        
    def _stage_one_over(self, data):
        name = data['machine']
        machine = self.mgr.get_machine(name)
        if machine.uuid:
            uuid = machine.uuid
            remove_pxeconfig(uuid)
            filename = pxeconfig_filename(uuid)
            if os.path.isfile(filename):
                raise RuntimeError, "%s still exists." % filename
            return
        
        addresses = self.mgr.list_machine_addresses(name)
        for address in addresses:
            remove_pxeconfig(address)
            filename = pxeconfig_filename(address)
            print "FILENAME: %s" % filename
            if os.path.isfile(filename):
                raise RuntimeError, "%s still exists." % filename
    
    def collection_post(self):
        data = self.request.json
        action = data['action']
        if action == 'submit':
            data = self._submit_machine(data)
        elif action == 'install':
            self._install_machine(data)
            data = dict(result='success')
        elif action == 'stage_over':
            self._stage_one_over(data)
            data = dict(result='success')
        return data
        
    def get(self):
        name = self.request.matchdict['name']
        return dict(name=name)
    
        
    
@resource(collection_path='/api0/addresses',
          path='/api0/addresses/{address}')
class AddressResource(object):
    def __init__(self, request):
        self.request = request
        self.db = self.request.db
        self.mgr = MachineAddressManager(self.db)

    def get(self):
        address = self.request.matchdict['address']
        name = self.mgr.identify_machine(address)
        if name is None:
            raise HTTPNotFound, "No machine found with %s" % name
        return dict(name=name)
    
        
        
