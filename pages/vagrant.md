# [Paella](#)

## Vagrant

### Introduction

Vagrant is used to establish a testing environment for paella.  The 
Vagrantfile creates a virtualbox machine with two network interfaces.  The 
second network is a virtualbox internal network where the installation system 
is hosted.  The installation system can be tested by creating virtual 
machines and booting from the internal network to define and install the 
system.

At the moment, there is only the proof of concept installer that installs a 
minimal i386 system.

### Set up the Environment

First you will need to have [Virtual Box](http://virtualbox.org) installed 
on your system.  Then make sure to download and
install [Vagrant](http://www.vagrantup.com/downloads.html) on your system.  I 
used version 1.5.1 when creating the system.  As of this writing, the 
current version is 1.5.3, which should work, as well as later versions 
1.x.x.  Once vagrant is installed, you will need two plugins.

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
security and salt repositories, is currently just over 600 megabytes 
in size.

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
vagrant reload
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

