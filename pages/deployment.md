# Outline

How is paella going to work?

Two deployment scenarios:

1. Set up a network in the office or workplace of a person who creates servers 
   for people.  This person can use paella to create fully configured machines 
   that can be physically carried and installed at another location.

2. Set up a network where the hosts on the network are installed and managed 
   by a paella server.

# Where is this stuff useful?

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

# Interesting Links

http://sourceforge.net/projects/unattended/

http://www.thewindowsclub.com/the-system-preparation-tool-sysprep-in-microsoft-windows-7

http://www.thinkwiki.org/wiki/Windows_PE

http://technet.microsoft.com/en-us/library/cc709665(WS.10).aspx

https://eldon.me/?p=73


DriverPacks with Sysprep

http://forum.driverpacks.net/viewtopic.php?id=4849

# Windows Stuff

## Netboot a PE environment

Use wimlib to make pe iso.
netboot iso and server iso http instead of tftp (ipxe or gpxe?)

or

Use PXE entirely, (seems that sending the winpe.wim will 
take too long).

## Configure PE environment

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
things will be ok.  It did!

## Learn GuiRunOnce

Attempt to stick python and autoit on the base system after install.

Every windows system will have python installed.  Autoit will either 
be installed permanently, or placed in a temporary location to 
execute the configuration scripts before being removed.  In this 
circumstance, the autoit binary will have to be provided by the 
configuration provisioner to execute the autoit scripts.


## Set up reference environment

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
	  
	- even if we can't do the bcd boot from wimlib, we can send 
	  a POST request to the server instructing it that we need 
	  a winpe system to boot next with a script that will execute
	  bcdboot properly then reboot back into the windows system.
	  
	- VirtualBox will be used to execute bcdboot in a winpe 
	  environment.  The live user needs to be a member of the 
	  disk group and possible a member of the fuse group
	  
	- There needs to be a way to determine whether or not 
	  the execution of bcdboot in virtualbox actually 
	  succeeded.
	  
	- Using virtualbox to prepare the machine to boot should 
	  be regarded as a temporary measure while an alternative 
	  method to prepare the machine for booting is pursued.
	  
	  
	  
	
	
## Look at using salt windows software repo

salt-minion on windows

preseeded keys can be included in winpe.iso

## Driverpacks

- slipstream driverpacks into iso

	- can this be done entirely within debian?
	
	- easily?
	
- use a samba share for the driverpacks

	- still need to have network drivers available beforehand
	
- store driverpacks installer in system wim

	- most every system should work, but wim is much larger
	
	- store driverpacks installer with local network drivers on system
	  wim, then driverpack install from samba share
	  
	  
	
	
### custom machines

A special unattend file and other scripts and files can be 
created on a special winpe iso for the target machine.  This 
will be done using mkwinpeimg.  The iso can be written to stdout 
making it easy to serve over http without making too many unnecessary 
temporary files.  The iso could be reached by a url 

/paella/api0/winpe/iso/install/{uuid}

This url can be place in the pxe config file



### another outline

- basic windows auto installer -> creates very basic system in audit mode

- use the basic windows auto installer to create base reference system

- create auto installer to install base reference system in audit mode

- the base reference system will make the useful images, which can 
  be categorized as needed
  

- debian live system installs reference image

	- still need to reboot to winpe to run bcdboot
	
	- think about using virtualbox to run a quick winpe
	  session to run bcdboot (all windows 7+ systems will
	  have enough memory to do this effectively).
	  
	  
	  
### more stuff

A machine now has an ostype property.  Now only supported is 
debian and win7.  OS type for debian machines may use release 
names.  The word debian should default to whatever is stable, or 
be deprecated and removed.  The win7 ostype is win7 ultimate, 
currently.  Devise manner for naming windows releases.

Another idea.  Have ostype be either debian or microsoft.  Have 
a release property that identifies the release of the ostype.
The microsoft machines also need WIM path for the image they will 
be using.


## Building Salt Minion on Windows 7

- Use MinGW as the toolchain.

- Use Msys for dev shell

- Install ActivePerl to build openssl

- Build openssl from source

- use openssl to build m2crypto
