# [Paella](#)

## NEWS

- Paella is being rewritten completely.  

- [Vagrant](http://www.vagrantup.com/) is being used to create a 
  testing environment.

- Currently using chef/debian-7.4 vagrant box 

- Using Debian Installer via PXE for first stage install

- Using [salt](http://saltstack.org/) for second stage
  installation and configuration.

- Using system [uuid's](#pages/system-uuid) to for machine 
  identification and network access.  MACs from ethernet interfaces
  are no longer required to identify machines. (Code to consistently
  generate a uuid based on network interfaces on machines lacking
  a SMBIOS to retrieve the system uuid from should be looked into
  using.  It is expected that most i386/amd64 machines will have
  a system uuid, however armhf (raspberrrypi) machines won't have
  this.

- Currently supporting i386 and amd64 debian installs.

- A preliminary environment exists to help manage windows 
  installations.  The installation of a customized system 
  can be performed automatically, but the system can, and 
  for the time being will have to be, configured manually 
  using sysprep.

- Web interface to help manage machines and configurations.  The web
  server uses [trumpet](https://github.com/umeboshi2/trumpet.git),
  which is a small collection of code to help make pyramid web services that
  support RESTful interaction.  The client side browser application uses the
  "paella" branch of [conspectus](https://github.com/umeboshi2/conspectus.git).
  
	  - Partition recipes and raid recipes are created and edited on web interface.

	  - Machines can be set/unset for installation.

	  - Architecture and OS type can be set.


## links

[Windows Deployment Services](http://en.wikipedia.org/wiki/Windows_Deployment_Services) to the network.

[debian wiki id systems](https://wiki.debian.org/HowToIdentifyADevice/System)

[generate unique id](http://unix.stackexchange.com/questions/144812/generate-consistent-machine-unique-id)

[wimboot](http://ipxe.org/wimboot) - boot wim images via pxe

[uefi-pxe-netboot-install](https://wiki.ubuntu.com/UEFI/PXE-netboot-install)

[uefi-pxe-win8](http://technet.microsoft.com/en-us/library/jj938037.aspx)

[Wikipedia article on PXE](http://en.wikipedia.org/wiki/Preboot_Execution_Environment)

[Wikipedia article on UEFI](http://en.wikipedia.org/wiki/Unified_Extensible_Firmware_Interface)

http://en.wikipedia.org/wiki/EFI_System_partition

http://en.wikipedia.org/wiki/GUID_Partition_Table

http://en.wikipedia.org/wiki/System_Management_BIOS

[virtualbox uefi support for windows guests]( https://www.virtualbox.org/ticket/7702)

[Protecting the pre-OS env with UEFI - building win8](http://blogs.msdn.com/b/b8/archive/2011/09/22/protecting-the-pre-os-environment-with-uefi.aspx)

[ubuntu secure boot](https://wiki.ubuntu.com/SecurityTeam/SecureBoot)

[reflections on trusting trust (reloaded)](https://www.hackinparis.com/sites/hackinparis.com/files/JohnButterworth.pdf)

