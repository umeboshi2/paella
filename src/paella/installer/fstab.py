

class Mount(object):
    def __init__(self, device, mpoint, type, options=['defaults'], dump=0, _pass=0):
        object.__init__(self)
        self.device = device
        self.mpoint = mpoint
        self.type = type
        self.options = options
        self.dump = dump
        self._pass = _pass

    def __repr__(self):
        fpart = '%s\t%s\t%s' % (self.device, self.mpoint, self.type)
        spart = '%s\t%s\t%s\t%s' % (fpart, ','.join(self.options), self.dump, self._pass)
        return spart

    def __str__(self):
        fpart = '%s\t%s\t%s' % (self.device, self.mpoint, self.type)
        spart = '%s\t%s\t%s\t%s' % (fpart, ','.join(self.options), self.dump, self._pass)
        return spart

class Proc(Mount):
    def __init__(self):
        Mount.__init__(self, 'proc', '/proc', 'proc')
        

class Tmp(Mount):
    def __init__(self):
        Mount.__init__(self, 'tmpfs', '/tmp', 'tmpfs')

class Swap(Mount):
    def __init__(self, device):
        Mount.__init__(self, device, 'swap', 'swap', 'swap')

class Dev(Mount):
    def __init__(self):
        Mount.__init__(self, 'devfs', '/dev', 'devfs')
        

class _Physical(Mount):
    def __init__(self, device, mpoint, type='reiserfs', options=['defaults']):
        Mount.__init__(self, device, mpoint, type, options=options)
        
class Root(_Physical):
    def __init__(self, device, type='reiserfs', options=['defaults']):
        _Physical.__init__(self, device, '/', type, options)

class Usr(_Physical):
    def __init__(self, device, type='reiserfs', options=['defaults']):
        _Physical.__init__(self, device, '/usr', type, options)
    
class Var(_Physical):
    def __init__(self, device, type='reiserfs', options=['defaults']):
        _Physical.__init__(self, device, '/var', type, options)

class Home(_Physical):
    def __init__(self, device, type='reiserfs', options=['defaults']):
        _Physical.__init__(self, device, '/home', type, options)
    

class _Fstab(object):
    def __init__(self):
        object.__init__(self)
        
    def __repr__(self):
        return '\n'.join(map(str, self._order_())) + '\n'

    def __str__(self):
        return '\n'.join(map(str, self._order_())) + '\n'

    


class SimpleFstab(_Fstab):
    def __init__(self, rdev):
        self.root = Root(rdev)
        self.proc = Proc()
        self.tmp = Tmp()

    def _order_(self):
        self.__order = [self.root, self.proc, self.tmp]
        return self.__order


class UmlFstab(_Fstab):
    def __init__(self, home='/dev/ubd1'):
        self.root = Root('/dev/ubd0', 'ext2')
        self.proc = Proc()
        self.dev = Dev()
        self.tmp = Tmp()
        self.home = Home(home, 'ext2')

    def _order_(self):
        self.__order = [self.root, self.proc, self.tmp]
        return self.__order
    
class HdFstab(SimpleFstab):
    def __init__(self):
        SimpleFstab.__init__(self, '_none_')
        self.root = Root('/dev/hda1', 'reiserfs')
        self.usr = Usr('/dev/hda5')
        self.var = Var('/dev/hda6')
        self.home = Home('/dev/hda7')

    def _order_(self):
        self.__order = [self.root, self.proc, self.tmp, self.usr, self.var, self.home]
        return self.__order


if __name__ == '__main__':
    fstab = []
    fstab.append(Root('/dev/hda1'))
    fstab.append(Proc())
    fstab.append(Swap('/dev/hda8'))
    fstab.append(Tmp())
    fstab.append(Usr('/dev/hda5'))
    fstab.append(Var('/dev/hda6'))
    fstab.append(Home('/dev/hda7'))
