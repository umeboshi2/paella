# Vagrant Salt Configuration

## What Vagrant Does

Paella starts by installing some basic packages that are either necessary
or useful.  Development packages and tools are necessary for preparing
paella to perform network intalls.




Shorewall
--------------

This is the firewall for paella.  In the vagrant development environment,
this state could very easily be replaced by a short iptables script
that performs the NAT. However, shorewall is a really good application
and the state helps serve to prepare other machines that will be using
shorewall.

DHCP and DNSServer
---------------------

One of the most difficult things to configure is the dhcp server.  In order to
support the various possibilities of pxe clients, as well as serve a
bootloader that is capable of retrieving images via http, the dhcpd
configuration can become quite involved, especially when
chainloading different bootfiles based upon client capabilities.  I
am attempting a generic configuration that will hopefully serve the proper
boot files regardless of pxe client, but it may be required for the system
administrator to reconfigure dhcpd to match their machines more closely.

The DNS is configured to respond the the hostname paella.  Dynamic updates
are also configured on DNS to allow for the minions to log to paella, but
this isn't fully implemented.


Samba (Optional)
-----------------------

Samba needs to be prepared in order to be able to install Microsoft Windows
systems.

The samba state, or configuration in salt for vagrant, can take quite a while
to execute.  The state is responsible for making sure that the files that
will be served through samba exist on the system, or otherwise retrieve
them from the internet.  The bulk of what is retrieved are two
windows 7 iso files from the Digital River site, as well as the
Windows Automatic Installation Kit iso available from Microsoft.  These
iso files can take extensive time to download.  There are also other
files and small utilities that are good to install on a windows
system that are included.  The files that are necessary to build the
salt-minion on windows, as well at the build dependencies are also
installed here.

After the iso files are downloaded, they are mounted loopback and served
through samba.

PostgreSQL
---------------------

This is the database that paella uses.

Debrepos
----------------

This state prepares the local partial debian and security repository,
the partial salt repository and a paella repository for locally built
packages.  This is the local debian mirror that everything is installed
from.  The desire is to have paella capable of fully automated installs
on a network that is disconnected from the internet.  This goal is not
being chased vigorously, but the foundation of the goal needs to be
prepared.


Virtualenv
-------------------

This state prepares the different python virtual environments that are used with
paella.


SaltMaster
-----------------

This state is responsible for installing the salt master.  Each machine
that is installed with paella will have salt-minion installed and the
salt master will configure those machines.


Main Server
-------------------

This state depends on apache, virtualenv, and postgresql.  This state
prepares the paella pyramid web server application and the paella database.
This state also depends on the webdev state that is responsible for building
the static resources for the web browser.

WimLib (Optional)
-----------------------

Wimlib is used to manage WIM images.  Wimlib is necessary to extract the
boot.wim from the AIK iso and create the WinPE iso used in paella.  The 
schroot and pbuilder packages are installed and configure to build wimlib
packages for i386 arch. The wimlib packages are uploaded to local
paella debrepos.

Paella Client
------------------

Paella client is a very simple command line tool to talk to the paella
server.  Currently it is the main manner to submit a new machine to
the paella database.  There is also a command to set the machine to be
installed, but not a command to unset a machine. 

WinPE (Optional)
--------------------

This state builds the WinPE iso files that will be used to instal windows
systems.  The example i386 iso file that is made will perform an automated
install.  An unattended file needs to be made for amd64 for the other iso
to do the same.

There is also an iso file created that executes bcdboot to install the
bootloader on windows installs.  This file is needed when using the wimlib
tools to install a WIM image to a hard drive.  After the image is
installed, a virtualbox instance is loaded that boots the iso and
installs the bootloader on the hard drive.

Debian Live
-------------------

Debian live systems are used with paella to assist with installs, management,
and other unforeseen tasks.  The live system has the command line tools to
submit a machine to the paella server.   It also has wimlib ready to install
[WIM](FIXME)images to the hard drive.  All the files and configuration to
build the live systems are installed with this set of states.

Driver Packs (Optional)
-----------------------------

When installing windows systems, drivers are necessary.  There are driver
packs available on the internet, and this state is written to retrieve
and prepare the driver packs for use with windows installs.  This is a work
in progress and unfinished.  Downloading the driver packs requires using
bittorrent.  I have written a python script that performs the job, however
with some service providers apparently blocking bittorrent traffic, an
alternative retrieval method should be explored.  It's possible that
preparing this part of paella may have to be left as an exercise for the
end user, with insructions given, rather than a completely automated
setup as desired.


Netboot
-------------

Much of the preparation described above is put together in the netboot
state.  This state prepares the debian installer in the tftpboot directory,
as well as building the debian live systems and installing those.  These
states also prepare tftpd-hpa and the other files in the tftpboot directory
that are served by tftpd.  A live system is built for each architecture.  This
state can take a while to complete.  This state also helps to make sure that
the tftpd service and nfsd service are configured and running properly.


Winbuilder (Optional)
--------------------------

This state will eventually be used to build the salt-minion for windows in
an automated manner.  There is an open github issue for this topic and
I desire to have this done at some point in my spare time.


By the time that the masterless salt provisioning in vagrant makes it to
the winbuilder state, the paella server should be fully prepared to start
executing network installs.

## Using Vagrant to bootstrap your network

While the vagrant development environment is a good tool to configure
and test paella, on normal virtualbox setups, it only installs to virtual
machines.

The vagrant machine can be used to install bare metal machines.  All that
is necessary is a secondary network interface on the host machine that
paella resides upon.  The Vagrantfile (FIXME) has a commented section
that will help configure the virtual machine to be bridged across the
secondary network interface on the host.  The host machine should be
configured statically.  If the paella server ip on it's local network is
10.0.4.1, the host machine should be set statically to 10.0.4.2, or
another appropriate ip that will not conflict with the dynamic addresses
the dhcp server provides to network clients.


