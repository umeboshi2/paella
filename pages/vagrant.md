# Vagrant

## Introduction

[Vagrant](https://vagrantup.com) is used to establish a testing
environment for paella.  The 
Vagrantfile creates a virtualbox machine with two network interfaces.  The 
second network is a virtualbox internal network where the installation system 
is hosted.  The installation system can be tested by creating virtual 
machines and booting from the internal network to define and install the 
system.

The vagrant virtual machine configuration is quite
[involved](#pages/saltconfig).  The default configuration
is to configure an http proxy for apt and install amd64
debian systems.  This is to ease the barrier for entry, as it can
take much time to configure the server completely to install the
full range of systems that lies within its capacity.

Formerly, the vagrant machine would make a local partial debian
mirror with reprepro for both wheezy and jessie, and for both
i386 and amd64 architectures.  The machine would also download
three very large microsoft iso files to perform the windows
installations.  I felt that this was too much of a requirement
for a person who would like to use paella, but didn't need all
of these requirements just to test the system.  I chose not to
use the i386 architecture as the default architecture, due to the
proliferation of amd64 machines.  With only the minimal requirements
prepared, the vagrant machine can be ready to be used much more quickly.

## Short Demonstration
<iframe width="560" height="315" src="https://www.youtube.com/embed/f0dlicdREEE" frameborder="0" allowfullscreen></iframe>

This is a very short demonstration of paella running in a vagrant environment.

## Set up the Environment

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

## Install a Machine

### Create a New Virtual Machine

In the Virtual Box Manager application, create a new machine.  Make 
sure it is set at Operating System: Linux, and Version: Debian.  Otherwise, 
the default settings in the wizard should be satisfactory.  You need to 
edit the settings of the machine and set the Network Adapter 1 to be attached 
to the Internal Network named "intloc."  If the vagrant machine is already 
provisioned, this network should already be selectable.

You may want to click on the System tab and enable Network in the Boot 
Order, and move it to the top.  If not, you will have to press F12 after 
powering the machine to boot from the network.

### Boot the Machine

Start the virtual machine and make sure it boots from the network.  If 
you are presented with a "First Run Wizard", you can press cancel as it 
will attempt to guide you into installing via a cdrom.  You should see a 
screen of paella and a ten second timer before the machine attempts to 
boot from the hard drive.  Press down and select "Standard Live System", 
and then the first entry on the next screen.  This will boot the live
system and allow you to identify the machine and set it to be installed.

### Using paella client

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

## Start the Install

Boot the machine from the network again, and you will see the install 
menu, with the install option as the first entry.  There is no timeout, 
so you must press enter for the machine to boot.  The machine will then 
boot into an automated debian install, then reboot back into a system 
that immediately engages in configuring itself using salt.


######## oldstuff



The VM will
be serving the files necessary to automatically install debian systems based
on either wheezy or jessie, and on either an i386 or amd64 architecture.  This
means that there are quite a few files to be downloaded and prepared before
the vagrant environment is operational.

Also, the paella server needs to download two windows 7 iso files, one for each
architecture, as well as the Windows Automated Installation Kit iso, for
retrieving the boot.wim file.  Moreover, there are quite a few windows
applications
that are also downloaded for use with paella.  Some of these are build and
runtime dependencies for the salt-minion, which will be used later to
automatically build the salt-minion windows package.

All in all, the vagrant machine will need to download approximately
15 gigabytes, more or less, of data from the internet.
**FIXME Check size of local repo.**

