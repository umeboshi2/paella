

class Network(object):
    def __init__(self, domain, ip_range):
        self.domain = domain
        self.network = ip_range
        


class Service(object):
    def __init__(self, name, port=None):
        object.__init__(self)
        self.name = name
        self.port = port
        self.zones = [Network('local', '127.0.0.0/8')]

        
        
class Server(object):
    def __init__(self, name):
        object.__init__(self)
        self.name = name
        self.services = []

    def add_service(self, service):
        self.services.append(service)

    


if __name__ == '__main__':
    s = Service('http', 80)
    
