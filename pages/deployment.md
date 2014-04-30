# [Paella](#)

## Outline

How is paella going to work?

Two deployment scenarios:

1. Set up a network in the office or workplace of a person who creates servers 
   for people.  This person can use paella to create fully configured machines 
   that can be physically carried and installed at another location.

2. Set up a network where the hosts on the network are installed and managed 
   by a paella server.

## Where is this stuff useful?

Paella is not designed for deploying debian systems in a cloud environment.  
There are plenty of tools to help with this, and ability to use 
[salt](saltstack.org), or another configuration system, is already 
generally available.  Paella, due to how it uses the debian installer 
in an automated fashion, could be useful in creating the base images that 
will be deployed in a cloud environment, but this is not why it was 
designed.

Paella could be very useful in server farms where machines are added and 
removed as needed.  Again, I didn't design paella for use in those 
environments, but it could be very easily done.  If each machine in the 
server farm was configured to boot from the network automatically, and 
the autoinstall property is set for each machine, the network can be 
completely managed remotely.

## Interesting Links

http://sourceforge.net/projects/unattended/

http://www.thewindowsclub.com/the-system-preparation-tool-sysprep-in-microsoft-windows-7

http://www.thinkwiki.org/wiki/Windows_PE

http://technet.microsoft.com/en-us/library/cc709665(WS.10).aspx

https://eldon.me/?p=73


DriverPacks with Sysprep

http://forum.driverpacks.net/viewtopic.php?id=4849

## Windows Stuff

### Netboot a PE environment

Use wimlib to make pe iso.
netboot iso and server iso http instead of tftp (ipxe or gpxe?)

or

Use PXE entirely, (seems that sending the winpe.wim will 
take too long).

### Configure PE environment

Another approach:  make custom winpe iso for each machine on demand.
Autounattend.xml for specific machine on iso root directory.
machine.ini for machine information

winpe environment script:

```
net use z: \\paella\win7
z:
setup.exe
```

Hopefully if windows installer picks up Autounattend.xml on cd drive
things will be ok.

Alternate idea:

Have the Autounattend.xml on the top directory of a samba share 
and map the drive before calling win7 setup.  This will be better 
if it works.  The docs I've read say that setup looks at the root 
directory of each bootable disk.  I am hoping that it looks at the 
root directory of each attached drive.



### Set up reference environment

- Use the automated install to install base system.

- Manually install the applications and configure the sytem.

- Use sysprep to prepare the system for capture.

- Reboot system from network to standard live system

- Use wimcapture to make .wim image of reference install

- Next boot the target machine and use imagex apply on drive

	- does it need partitioning/formatting?  Should we do this 
	  setup-storage from FAI or write some tools?  Using debian
	  servers eliminates some of the necessity for complex drive
	  systems on the windows hosts.
	
	- can we do the bcdboot stage with wimlib?  If not we need to 
	  boot into WinPE environment and use it there.
	  
