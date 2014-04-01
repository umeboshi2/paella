import os
from ConfigParser import ConfigParser

default_config = """[DEFAULT]
dist = squeeze
binary_images = net
bootloader = syslinux
chroot_filesystem = squashfs
architectures = amd64
mirror = http://refurby/debrepos/debian
mirror_security = http://refurby/debrepos/security
linux_flavours_i386 = 686 486

net_root_server = 10.0.2.1

current_arch = NOarch

[installer]
architectures = i386 amd64
machine = refurby_installer
net_root_path = /freespace/netboot/installer/%(current_arch)s
username = paella
syslinux_menu_entry = Paella Installer %(current_arch)s

[snoopy]
architectures = amd64
machine = snoopy
net_root_path = /freespace/netboot/snoopy/%(current_arch)s
syslinux_menu_entry = Snoopy Small System %(current_arch)s


"""
config_path = 'config/machines'

class PaellaLiveSystemConfig(ConfigParser):
    def get_archs(self, machine):
        return self.get(machine, 'architectures').split()
    

def generate_default_config(path):
    if not os.path.exists(path):
        dirname = os.path.dirname(path)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        cfile = file(path, 'w')
        cfile.write(default_config)
        cfile.close()


def get_config():
    filename = os.path.join(config_path, 'config.cf')
    generate_default_config(filename)
    cfile = file(filename)
    cfg = PaellaLiveSystemConfig()
    cfg.readfp(cfile)
    return cfg

template_config = get_config()

if __name__ == "__main__":
    tc = template_config
    
