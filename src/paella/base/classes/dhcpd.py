from operator import add

from paella.base.contrib.IPy import IP

global_dictlist = [
    {'ddns-update-style':'interim'},
    {'ddns-updates':'on'},
    {'do-forward-updates':'on'},
    {'update-optimization':'off'},
    {'update-static-leases':'on'},
    {'use-host-decl-names':'on'},
    {'default-lease-time':'600'},
    {'max-lease-time':'7200'},
    {'authoritative':''},
    {'log-facility':'local7'}
    ]

class SubNet(object):
    def __init__(self, net, bitmask):
        object.__init__(self)
        self._ip_ = IP('%s/%s' %(net, bitmask))

    def router(self):
        return self._ip_[1]

    def __getitem__(self, key):
        return self._ip_[key+1]

    def netmask(self):
        return self._ip_.netmask()

    def net(self):
        return self._ip_.net()

    def broadcast(self):
        return self._ip_.broadcast()
    
    

def brace(block):
    return '{\n%s\n}\n' %block

def endline(line):
    return '%s;\n' %line

def bracelines(lines):
    return brace(reduce(add, map(endline, lines)))

def range(low, high):
    return 'range %s %s' %(low, high)

def mac(macaddr):
    return 'hardware ethernet %s' %macaddr

def fixedaddr(ipaddr):
    return 'fixed-address %s' %ipaddr

def option(param, value):
    return 'option %s %s' %(param, value)

def parameter(param, value):
    return endline('%s %s' %(param, value))

def parameters(dictlist):
    return ''.join([parameter(p,v) for p,v in [ x.items()[0] for x in dictlist]])


def option_rtr(router):
    return option('routers', router)

def subnet(network, bitmask, options):
    pass

def fixed_host(hostname, macaddr, ipaddr, router):
    lines = [mac(macaddr), fixedaddr(ipaddr), option_rtr(router)]
    return 'host %s %s' %(hostname, bracelines(lines))


if __name__ == '__main__':
    fh = fixed_host('paella', '23:34:45:57:35', '10.0.0.34',  '10.0.0.1')
    ip = SubNet('10.0.0.0','24')
    
