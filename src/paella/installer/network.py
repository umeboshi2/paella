
class Interface(object):
    def __init__(self, name, config, address=None,
                 netmask=None, gateway=None, family='inet'):
        self.name = name
        self.config = config
        self.address = address
        self.netmask = netmask
        self.gateway = gateway
        self.family = family

    def _cline_(self, name, value):
        return '\t%s %s\n' % (name, value)

    def __repr__(self):
        return self._make_string_()
    
    def _make_string_(self):
        iface = 'iface %s %s %s\n' % (self.name, self.family, self.config)
        if self.config == 'static':
            config = self._cline_('address', self.address)
            config += self._cline_('netmask', self.netmask)
            if self.gateway:
                config += self._cline_('gateway', self.gateway)
            iface += config
        return iface

    def __str__(self):
        return self._make_string_()


class Interfaces(object):
    def __init__(self):
        self._interfaces = [('lo', Interface('lo', 'loopback'))]
        self._auto = ['lo']
        self._set_interfaces()

    def _set_interfaces(self):
        self.iface = dict(self._interfaces)

    def add(self, name, config, address=None, netmask=None,
            gateway=None):
        if name not in self.iface:
            self._interfaces.append((name, Interface(name, config, address,
                                              netmask, gateway)))
            self._set_interfaces()

    def set_auto(self, name):
        if name not in self._auto and name in self.iface:
            self._auto.append(name)
            

    def __repr__(self):
        output = 'auto %s\n' % ' '.join(self._auto)
        for name, iface in self._interfaces:
            output += str(iface)
        return output


if __name__ == '__main__':
    i = Interfaces()
    
    
