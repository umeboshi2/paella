from cornice.resource import resource, view


from paella.managers.main import MachineAddressManager

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
    
    def collection_post(self):
        name = self.request.json['name']
        addresses = self.request.json['addresses']
        data = self.mgr.add_new_machine(name, addresses)
        data['machine'] = data['machine'].serialize()
        data['addresses'] = [a.serialize() for a in data['addresses']]
        data['result'] = 'success'
        return data
        
    def collection_put(self):
        raise RuntimeError, "Not implemented"

    def put(self):
        raise RuntimeError, "Not implemented"

    def get(self):
        name = self.request.matchdict['name']
        raise RuntimeError, "Not implemented"
        
    
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
    
        
        
