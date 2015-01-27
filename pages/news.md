# NEWS

- Paella has been rewritten completely.  

- [Vagrant](http://www.vagrantup.com/) is being used to create a 
  development environment.

- Currently using chef/debian-7.4 vagrant box (amd64)

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

