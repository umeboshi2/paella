# [Paella](#)

## Vagrant

### Introduction

Vagrant is used to establish a testing environment for paella.  The 
Vagrantfile creates a virtualbox machine with two network interfaces.  The 
second network is a virtualbox internal network where the installation system 
is hosted.  The installation system can be tested by creating virtual 
machines and booting from the internal network to define and install the 
system.

The vagrant virtual machine configuration is quite involved.  The VM will
be serving the files necessary to automatically install debian systems based
on either wheezy or jessie, and on either an i386 or amd64 architecture.  This
means that there are quite a few files to be downloaded and prepared before
the vagrant environment is operational.

Also, the paella server needs to download two windows 7 iso files, one for each
architecture, as well as the Windows Automated Installation Kit iso, for
retrieving the boot.wim file.  Moreover, there are quite a few windows applications
that are also downloaded for use with paella.  Some of these are build and
runtime dependencies for the salt-minion, which will be used later to
automatically build the salt-minion windows package.

All in all, the vagrant machine will need to download approximately
15 gigabytes, more or less, of data from the internet.
**FIXME Check size of local repo.**

### Set up the Environment

First you will need to have [Virtual Box](http://virtualbox.org) installed 
on your system.  Then make sure to download and
install [Vagrant](http://www.vagrantup.com/downloads.html) on your system.  I 
used version 1.5.1 when creating the system.  As of this writing, the 
current version in debian jessie will work, as well as later versions 
1.x.x.  Once vagrant is installed, you will need two plugins.  If you are using
the vagrant found in debian jessie, you can skip the plugin installation.


```sh
vagrant plugin install vagrant-vbguest
vagrant plugin install vagrant-salt
```

Then in the project directory:

```sh
vagrant up
```

Depending upon the speed of your network connection, the configuring 
of the virtual machine can take a while.  The small partial debian 
repository necessary for a simple environment, along with the 
security and salt repositories, is currently just over 2000 megabytes 
in size. **FIXME Check size of local repo.**

There could be various problems that are reported by the salt provisioner, 
depending on the availability of network resources.  Most of the problems 
should be resolvable by executing:

```sh
vagrant provision
```

repeatedly until salt reports no errors.  If there were problems when 
initially updating the debian repositories, you may have to update them 
later.  The salt states that manage reprepro could use some work.  The 
building of the live system will depend on the repositories being updated 
and ready.  Otherwise, the state system will get almost everything else 
ready.

Once the salt provisioner reports no errors, you will have to reboot the 
virtual machine by typing:

```sh
vagrant reload --provision
```

When the machine boots again, the system should be ready.

### Install a Machine

#### Create a New Virtual Machine

In the Virtual Box Manager application, create a new machine.  Make 
sure it is set at Operating System: Linux, and Version: Debian.  Otherwise, 
the default settings in the wizard should be satisfactory.  You need to 
edit the settings of the machine and set the Network Adapter 1 to be attached 
to the Internal Network named "intloc."  If the vagrant machine is already 
provisioned, this network should already be selectable.

You may want to click on the System tab and enable Network in the Boot 
Order, and move it to the top.  If not, you will have to press F12 after 
powering the machine to boot from the network.

#### Boot the Machine

Start the virtual machine and make sure it boots from the network.  If 
you are presented with a "First Run Wizard", you can press cancel as it 
will attempt to guide you into installing via a cdrom.  You should see a 
screen of paella and a ten second timer before the machine attempts to 
boot from the hard drive.  Press down and select "Standard Live System", 
and then the first entry on the next screen.  This will boot the live
system and allow you to identify the machine and set it to be installed.

#### Using paella client

When the live system boots up, you can type:

```sh
paella-submit-machine <name>
```

where &lt;name&gt; is the name you wish to give the machine to identify it 
by.  This will send an http post request to the server with the name 
and the system uuid of the machine.  The system uuid will be used to 
create a special pxe config file that will be presented to the machine 
when it is set to be installed.  

After this, type:

```sh
paella-set-install
```

This will use the system-uuid to look up the machine in the database and 
tell the server to create the special pxe config file for the machine.  
Once this command successfully completes, you can reboot the machine.

### Start the Install

Boot the machine from the network again, and you will see the install 
menu, with the install option as the first entry.  There is no timeout, 
so you must press enter for the machine to boot.  The machine will then 
boot into an automated debian install, then reboot back into a system 
that immediately engages in configuring itself using salt.


## What Vagrant Does

Paella starts by installing some basic packages that are either necessary
or useful.  Development packages and tools are necessary for preparing
paella to perform network intalls.




Shorewall
--------------

This is the firewall for paella.  In the vagrant development environment, this state
could very easily be replaced by a short iptables script that performs the NAT.
However, shorewall is a really good application and the state helps serve to
prepare other machines that will be using shorewall.

DHCP Server
-------------------

One of the most difficult things to configure is the dhcp server.  In order to
support the various possibilities of pxe clients, as well as serve a bootloader that
is capable of retrieving images via http, the dhcpd configuration can become
quite involved, especially when chainloading different bootfiles based upon client
capabilities.  I am attempting a generic configuration that will hopefully serve the
proper boot files regardless of pxe client, but it may be required for the system
administrator to reconfigure dhcpd to match their machines more closely.

Samba
----------

Samba needs to be prepared in order to be able to install Microsoft Windows systems.

The samba state, or configuration in salt for vagrant, can take quite a while to
execute.  The state is responsible for making sure that the files that will be served
through samba exist on the system, or otherwise retrieve them from the internet.  The
bulk of what is retrieved are two windows 7 iso files from the Digital River site, as well
as the Windows Automatic Installation Kit iso available from Microsoft.  These iso files
can take extensive time to download.  There are also other files and small utilities
that are good to install on a windows system that are included.  The files that
are necessary to build the salt-minion on windows, as well at the build dependencies
are also installed here.

After the iso files are downloaded, they are mounted loopback and served
through samba.

PostgreSQL
---------------------

This is the database that paella uses.

Debrepos
----------------

This state prepares the local partial debian and security repository, the partial
salt repository and a paella repository for locally built packages.  This is the
local debian mirror that everything is installed from.  The desire is to have
paella capable of fully automated installs on a network that is disconnected
from the internet.  This goal is not being chased vigorously, but the foundation
of the goal needs to be prepared.


Virtualenv
-------------------

This state prepares the different python virtual environments that are used with
paella.


SaltMaster
-----------------

This state is responsible for installing the salt master.  Each machine that is
installed with paella will have salt-minion installed and the salt master will
configure those machines.


Main Server
-------------------

This state depends on apache, virtualenv, and postgresql.  This state
prepares the paella pyramid web server application and the paella database.
This state also depends on the webdev state that is responsible for building
the static resources for the web browser.

WimLib
-----------

Wimlib is used to manage WIM images.  Wimlib is necessary to extract the
boot.wim from the AIK iso and create the WinPE iso used in paella.  The 
schroot and pbuilder packages are installed and configure to build wimlib
packages for i386 arch. The wimlib packages are uploaded to local paella debrepos.

Paella Client
------------------

Paella client is a very simple command line tool to talk to the paella server.  Currently
it is the main manner to submit a new machine to the paella database.  There is
also a command to set the machine to be installed, but not a command to unset a
machine. 

WinPE
---------

This state builds the WinPE iso files that will be used to instal windows
systems.  The example i386 iso file that is made will perform an automated
install.  An unattended file needs to be made for amd64 for the other iso
to do the same.

There is also an iso file created that executes bcdboot to install the bootloader
on windows installs.  This file is needed when using the wimlib tools to install
a WIM image to a hard drive.  After the image is installed, a virtualbox instance
is loaded that boots the iso and installs the bootloader on the hard drive.

Debian Live
-------------------

Debian live systems are used with paella to assist with installs, management,
and other unforeseen tasks.  The live system has the command line tools to
submit a machine to the paella server.   It also has wimlib ready to install wim
images to the hard drive.  All the files and configuration to build the live systems
are installed with this set of states.

Driver Packs
-------------------

When installing windows systems, drivers are necessary.  There are driver
packs available on the internet, and this state is written to retrieve and prepare
the driver packs for use with windows installs.  This is a work in progress and
unfinished.  Downloading the driver packs requires using bittorrent.  I have
written a python script that performs the job, however with some service
providers apparently blocking bittorrent traffic, an alternative retrieval method
should be explored.  It's possible that preparing this part of paella may have to
be left as an exercise for the end user, with insructions given, rather than a
completely automated setup as desired.


Netboot
-------------

Much of the preparation described above is put together in the netboot
state.  This state prepares the debian installer in the tftpboot directory,
as well as building the debian live systems and installing those.  These
states also prepare tftpd-hpa and the other files in the tftpboot directory
that are served by tftpd.  A live system is built for each architecture.  This
state can take a while to complete.  This state also helps to make sure that
the tftpd service and nfsd service are configured and running properly.


Winbuilder
----------------

This state will eventually be used to build the salt-minion for windows in
an automated manner.  There is an open github issue for this topic and
I desire to have this done at some point in my spare time.


By the time that the masterless salt provisioning in vagrant makes it to
the winbuilder state, the paella server should be fully prepared to start
executing network installs.

## Using Vagrant to bootstrap your network

While the vagrant development environment is a good tool to configure
and test paella, on normal virtualbox setups, it only installs to virtual machines.

The vagrant machine can be used to install bare metal machines.  All that
is necessary is a secondary network interface on the host machine that
paella resides upon.  The Vagrantfile (FIXME) has a commented section
that will help configure the virtual machine to be bridged across the
secondary network interface on the host.  The host machine should be
configured statically.  If the paella server ip on it's local network is
10.0.4.1, the host machine should be set statically to 10.0.4.2, or
another appropriate ip that will not conflict with the dynamic addresses
the dhcp server provides to network clients.


