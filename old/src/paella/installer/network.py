
IFACEATTRIBUTES = ['pre-up', 'up', 'post-up', 'down', 'pre-down', 'post-down']
IFACE_OBJECT_ATTRIBUTES = [att.replace('-', '_') for att in IFACEATTRIBUTES]
IFACE_ATTRIBUTE_DICT = dict(zip(IFACEATTRIBUTES, IFACE_OBJECT_ATTRIBUTES))

class BaseInterface(object):
    def __init__(self, name, family='inet', method=None):
        self.name = name
        self.family = family
        self.method = method
        self.pre_up = None
        self.up = None
        self.post_up = None
        self.down = None
        self.pre_down = None
        self.post_down = None
        self._method_opts = []
        self._method_optdict = {}
        
    def append_option(self, name, value=None):
        self._method_opts.append(name)
        self._method_optdict[name] = value
        
    def set_option(self, name, value):
        if name in self._method_opts:
            self._method_optdict[name] = value
        elif name in IFACE_OBJECT_ATTRIBUTES:
            setattr(self, name, value)
        elif name in IFACEATTRIBUTES:
            setattr(self, IFACE_ATTRIBUTE_DICT[name], value)
        else:
            raise RuntimeError , 'Unknown option %s' % name

    def list_command_options(self):
        return [opt for opt in IFACE_OBJECT_ATTRIBUTES]

    def list_method_options(self):
        return [opt for opt in self._method_opts]
    
    def list_options(self):
        return self.list_command_options() + self.list_method_options()
    
    
    def _stanza(self):
        lines = []
        lines.append(self._iface_line())
        for opt in self._method_opts:
            value = self._method_optdict[opt]
            if value is not None:
                lines.append(self._cline_(opt, value))
        for attribute in IFACEATTRIBUTES:
            value = getattr(self, IFACE_ATTRIBUTE_DICT[attribute])
            if value is not None:
                lines.append(self._cline_(attribute, value))
        return lines
    
    def _iface_line(self):
        if self.method is None:
            raise RuntimeError , "method not set for %s interface" % self.name
        line = 'iface %s %s %s\n' % (self.name, self.family, self.method)
        return line
    
    def _cline_(self, name, value):
        return '\t%s %s\n' % (name, value)

    def _make_string_(self):
        return ''.join(self._stanza())
    
    def __repr__(self):
        return self._make_string_()
    
    def __str__(self):
        return self._make_string_()


class LoopbackInterface(BaseInterface):
    def __init__(self, name='lo'):
        BaseInterface.__init__(self, name=name, family='inet', method='loopback')

class BaseEthernetInterface(BaseInterface):
    def __init__(self, name='eth0', method=None):
        BaseInterface.__init__(self, name=name, family='inet', method=method)
        
class StaticEthernetInterface(BaseEthernetInterface):
    def __init__(self, name='eth0'):
        BaseEthernetInterface.__init__(self, name=name, method='static')
        for opt in ['address', 'netmask', 'broadcast', 'network', 'metric',
                    'gateway', 'pointopoint', 'media', 'hwaddress', 'mtu']:
            self.append_option(opt)

class DHCPEthernetInterface(BaseEthernetInterface):
    def __init__(self, name='eth0'):
        BaseEthernetInterface.__init__(self, name=name, method='dhcp')
        for opt in ['hostname', 'leasehours', 'leasetime', 'vendor',
                    'client', 'hwaddress']:
            self.append_option(opt)
            
class PPPInterface(BaseInterface):
    def __init__(self, name='ppp0'):
        BaseInterface.__init__(self, name=name, family='inet', method='ppp')
        self.append_option('provider')

# this class should not be called alone
# the __init__ is to be called after the __init__
# of one of the ethernet interfaces.  This class
# exists as a convenient way to add the bridging
# options to the other ethernet interfaces
class BaseBridgedInterface(object):
    def __init__(self, name='br0'):
        if not hasattr(self, '_method_opts'):
            msg = "This init method must be called after the init of a BaseInterface"
            raise RuntimeError , msg
        for opt in ['ports', 'ageing', 'bridgeprio', 'fd', 'gcint',
                    'hello', 'hw', 'maxage', 'maxwait', 'pathcost', 'portprio',
                    'stp', 'waitport']:
            bropt = 'bridge_%s' % opt
            self.append_option(bropt)
            
class StaticBridgedInterface(StaticEthernetInterface, BaseBridgedInterface):
    def __init__(self, name='br0'):
        StaticEthernetInterface.__init__(self, name=name)
        BaseBridgedInterface.__init__(self, name=name)

class DHCPBridgedInterface(DHCPEthernetInterface, BaseBridgedInterface):
    def __init__(self, name='br0'):
        DHCPEthernetInterface.__init__(self, name=name)
        BaseBridgedInterface.__init__(self, name=name)
        

            
class InterfacesOld(object):
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


# this dictionary helps map methods
# to the classes
METHODS = dict(loopback=LoopbackInterface,
               dhcp=DHCPEthernetInterface,
               static=StaticEthernetInterface,
               brstatic=StaticBridgedInterface,
               brdhcp=DHCPBridgedInterface,
               ppp=PPPInterface)


if __name__ == '__main__':
    ifdict = IFACE_ATTRIBUTE_DICT
    lo = LoopbackInterface()
    eth0 = DHCPEthernetInterface()
    eth1 = StaticEthernetInterface('eth1')
    ppp = PPPInterface()
    ppp.set_option('provider', 'dsl-provider')
    
    br0 = StaticBridgedInterface()
