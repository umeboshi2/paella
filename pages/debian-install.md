# Debian Installer

When paella was first created, the debian installer was not the modular and
highly configurable application that it is now.  It was generally less trouble to
use a live system to partition the disk, debootstrap a system, install packages,
then configure the kernel and bootloader.  A live system was, and still is, far more
flexible and easier to manipulate than the debian installer.

Through a careful use of the kernel command line, special preseed files, as well
as early and late scripts, the debian installer can be used as a predictable
application where much effort has been spent on successfully installing a system
where the hardware, disk configuration, and boot methods can vary considerably.
While the debian installer system is very limited with respect to a full featured
debian-live system, it has the advantage of being easier to maintain consistent
installation quality with relatively low maintainence.  There are a larger number
of people making sure the debian installer works correctly, than the number of
people who are concerned that a custom system installs a debian system correctly.

