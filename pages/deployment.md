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

