# [Paella](#)

## NEWS

- Paella is being rewritten completely.  

- [Vagrant](http://www.vagrantup.com/) is being used to create a 
  testing environment.

- Currently using i386 vagrant box running debian/wheezy

- Using Debian Installer via PXE for first stage install

- Using [salt](http://saltstack.org/) for second stage
  installation and configuration.

- Using system [uuid's](#pages/system-uuid) to for machine 
  identification and network access.

- Investigating using samba with the rest of the stack to 
  provide
[Windows Deployment Services](http://en.wikipedia.org/wiki/Windows_Deployment_Services) to the network.

