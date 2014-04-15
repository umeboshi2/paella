import os
import json

from pyramid.exceptions import HTTPNotFound
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
        pass

    def _submit_machine(self, data):
        name = data['machine']
        addresses = data['addresses']
        # add machine
        data = self.mgr.update_machine(name, addresses)
        # FIXME
        if data is not None:
            data['machine'] = data['machine'].serialize()
            data['addresses'] = [a.serialize() for a in data['addresses']]
        return data

    def _install_machine(self, data):
        name = data['machine']
        addresses = self.mgr.list_machine_addresses(name)
        for address in addresses:
            make_pxeconfig(address, name)
            filename = pxeconfig_filename(address)
            print "FILENAME: %s" % filename
            if not os.path.isfile(filename):
                raise RuntimeError, "%s doesn't exist." % filename
            
        
        
    def collection_post(self):
        data = self.request.json
        action = data['action']
        if action == 'submit':
            data = self._submit_machine(data)
        elif action == 'install':
            self._install_machine(data)
            data = dict(result='success')
        elif action == 'stage_over':
            raise RuntimeError, "Not implemented"
        
        return data
        
    def collection_put(self):
        raise RuntimeError, "Not implemented"

    def put(self):
        raise RuntimeError, "Not implemented"

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
    
        
        
