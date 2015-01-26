# PXE Issues

Netbooting varies from machine to machine.  There are many machines that will 
not boot from the network unless a key, like F12, is pressed during the 
preboot.  Other machines will readily boot from the network as the first 
boot option.  The default pxe configuration file will default to booting 
from the first hard drive automatically after a ten second delay.  

When a machine is set to be installed, the machine's specific pxe 
configuration file will default to booting the installer, and by 
default wait for a console user to press enter on the keyboard.

There is an autoinstall option that will configure the machine's specific 
pxe file to boot without needing a console user to press a key, probably 
with a five to ten second delay.

# iPXE

I need to mention [iPXE](https://ipxe.org).  iPXE is a replacement
pxe image for common pxe clients.  The iPXE code provides for retrieving the
bootloader over the network using modern protocols, as well as the standard
tftp protocol.

# UEFI

After looking at the debian installer for a while, it seems that in order to
boot UEFI enabled clients, a small swarm of efi modules may be necessesarily
placed somwhere in the tftpboot directory.

After looking at a couple of laptops, the bigger problem seems to be how
to enable netboot on these machines.  It seems that a network efi module
must be installed manually on these systems before the system can boot
from the network.
