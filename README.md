# Paella


## Introduction 

Paella is a system for that has been used to install preconfigured 
debian systems over a local network in a manner similar to FAI_.  The 
project started in 2004 as a set of scripts within the FAI installer than 
communicated with a PostgreSQL database to retrieve the configuration for 
the target machine.

The old website for this project is at http://paella.berlios.de

## NEWS

- Paella is being rewritten completely.  

- [Vagrant](http://www.vagrantup.com/) is being used to create a 
  testing environment.

- Currently using i386 vagrant box running debian/wheezy

- Using Debian Installer via PXE for first stage install

- Using [salt](http://saltstack.org/) for second stage
  installation and configuration.

## Vagrant

Vagrant is used to establish a testing environment for paella.  The 
Vagrantfile creates a virtualbox machine with two network interfaces.  
The second network is a virtualbox internal network where the installation 
system is hosted.  The installation system can be tested by creating virtual 
machines and booting from the internal network to define and install the 
system.

At the moment, there is only the proof of concept installer that installs a 
minimal i386 system.

## Outline

How is paella going to work?

Two deployment scenarios:

1. Set up a network in the office or workplace of a person who creates servers 
   for people.  This person can use paella to create fully configured machines 
   that can be physically carried and installed at another location.

2. Set up a network where the hosts on the network are installed and managed 
   by a paella server.

### System UUID

The machines on the paella network are identified by their system 
uuid.  In normal network operations, AFAICT, the system uuid is only 
transferred over the network during the PXE negotiation, in plaintext.  
When using paella, the uuid, is transferred over the network in http 
requests by the client when identifying itself to the server.  The paella 
database should not provide a uuid to a paella client.

Even though paella is really meant to be used on a local network where 
the administrator has enough physical access and monitoring ability to 
provide trust during a network install, it would be valuable to raise 
the bar of an attacker to the point of having to discover or guess a 
system uuid.  Due to the nature of PXE, attempts to write code that 
would block an attacker that sniffs the network would be pointless.  
The design is mostly to keep a user of one machine to be able to 
retrieve the pillar data or minion keys of another machine.

### Pillar Data

The default pillar data is in a git repository.  I desire for these pillar 
files, eventually, to be python scripts that access a database using 
SQLAlchemy.

There are currently other problems with having the data in a pillar.  The 
ability to refer to pillar keys within the pillar is not directly 
available.  Due to the fact that pillar data is basically a set of nested 
dictionaries, it should be possible to achieve the desired results through 
a different pillar rendering system.

### Install Routine

#### Default Live System

Boot a machine over the network.  The default boot menu will allow you to 
boot into a live system where you can identify the machine and set a flag 
on the server to install the machine.

Two scripts on the live system:

1. paella-submit-machine <name>
   
   1. sends a name to the server
   
	   - actually sends json.dumps(
		 dict(action='submit', machine=name, addresses=[a1, a2]))
		 in a POST request to http://host/paella/machines
   
   2. the salt config should already have this name
   
   3. all mac addresses sent to server and tied to name
   

2. install-machine
   
   1. machine must already be submitted by script above
   
   2. name lookup based on matching mac address
   
   3. the script gets addresses on local machine then checks 
   http://host/paella/addresses/{address} for a machine name, 
   accepting the first match.
		 
   4. after a successful match, the retrieved machine name is sent 
   in a POST request dict(action='install', machine=name) to
   http;//host/paella/machines .
   
   5. The request above tells the server to create special pxe config 
   files named after the mac addresses linked to the machine in the 
   database.
   
   6. The distinctive feature of the specific pxe config file for the
   mac address of the target machine is that appends a preseed 
   url to the kernel command line specific to the machine.
   
	   - http://host/paella/preseed/{machine}
	   
   7. It is the preseed file's duty to make sure salt-minion is installed,
   and the machine identified for the minion to work.  This is currently being 
   done using hostname.

#### General Install Procedure  

Procedure when the machine is introduced to the network:

1. Boot machine from network into live system.

2. At command prompt type: paella-submit-machine <name>
   where <name> is the name of the machine.
   
3. Next, type: paella-set-install.  This will instruct 
   the server to create pxe config files for the mac 
   addresses of the machine.

Procedure when machine set to be installed:
 
1. Boot machine from network.  The pxe menu will have an install
   entry at the top that provides the installer with a preseed file 
   generated for the machine.  The user must press enter to boot debian 
   pxe image.
 
2. The machine will then boot the standard debian installer and install 
   a basic system.  The preseed file should provide a way through the 
   early command to send a recipe file to the installer system.  At the 
   moment, the only filesystem being used is the atomic/lvm as provided 
   in the standard debian example preseed file.
 
3. The debian installer will also install salt-minion.  

4. The late command will retrieve a script from the server and 
   execute it.  This script is responsible for identifying the 
   machine for the salt master.  The script will be rendered from 
   a mako template server side with the information that identifies 
   the machine.  The actual identifier of the machine is the URL 
   from where the script is retrieved.
   
5. The script will also send a POST request to the server instructing it 
   that the debian install procedure is about to complete.  The server will 
   then remove the pxe config files.

6. Once the late command finishes, the debian installer tidies up and 
   unmounts the filesystems, then reboots.  If the machine doesn't default 
   to booting from the network and will boot from the hard drive, the 
   second stage of the installation will continue.  If the machine boots 
   from the network, the default menu option is to boot from the hard 
   drive.
   
 
### PXE Issues

Netbooting varies from machine to machine.  There are many machines that will 
not boot from the network unless a key, like F12, is pressed during the 
preboot.  

Other machines will readily boot from the network at first option.  I intend 
for paella to be flexible enough to handle these situations.  The default 
pxe config file will default to booting from the first hard drive 
automatically after a ten second delay.  A machine that boots from the 
network by default, or as the first boot device, will effectively 
default to booting from their first hard drive.


### Preseed builder

The preseed is currently a mako template.  

The preseed file has certain responsibilities beyond automating the first 
stage of the installation.

1. The early command must download and execute a  script that:

	1. Determines the partman recipe for the machine and installs it 
	to the installer filesystem (/tmp/disk-recipe).
	
	2. Overrides the archive.gpg in the installer environment with the 
	key from the local repository.  (This is still problematic and the 
	first stage install is still unauthenticated.)
	
2. The preseed file must install salt-minion.

3. The late command must download and execute a script that:

	1. Configures salt-minion with the identity of the machine.
	
	2. Send a post request to the server informing it that stage one is almost
	complete.  This will cause the server to delete the pxe config files 
	(or alternatively, reconfigure the files to default to hard drive booting).

	3. Preseeds the salt-minion with the installer keys. (This isn't implemented
	yet.  The master is running in open mode.)  The request made above should 
	signal the server to locate the minion keys for the machine, and if no 
	keys are found, to generate them.  The paella server should keep track of 
	all the keys and only set the master to accept those that it preseeds.
	


## TODO

- DONE: Make scripts for live netboot system to identify machines and set
  for install.
  
- DONE: Make server that accepts POST requests and assigns machine names 
  to mac addresses.
  
- DONE: Get server to render preseed files based on name of machine.

- DONE: Get server to create and destroy pxe config files for machines in 
  /var/lib/tftpboot.

- Setup scripts to help with partial repository STARTED

- Move more info into pillar data

  - wipe out all hardcoded entries of '10.0.4.1' to config files or pillar data

- Create some simple disk/partition recipes to use as a starting 
  point.
  
- Automate key generation and preseed the keys during first stage 
  install.
  http://docs.saltstack.com/en/latest/topics/tutorials/preseed_key.html

- DONE: use system uuid instead of mac addresses: dmidecode -s system-uuid




## History

### What was it?

Paella was written over eight years ago, yet much of the core components 
have changed little since the project started approaching stability.  Some 
of the core code was removed into the useless project for use in other 
projects unrelated to paella.  The latest major change the the code was 
made in 2009, and I have been using paella to install systems consistently 
since then.  The code has proven itself to be a reliable framework, where 
the changes that are necessary to update the manner in which the installer 
operates can be handled through the hooks that the installer objects 
provide.

The other edge of this sword is that, in the attempt to design a flexible 
framework that can be directed almost entirely through the configuration, 
the code that actually executes the framework has remained sessile.  While 
this provides stability and predictability, it comes at a price.  At this 
point in time, many of the upstreams sources that paella depends upon have 
all been deprecated by world developers at large, in favor of sources that 
are being actively developed and maintained.  This effectively puts the 
future of paella in jeopardy if the framework isn't eventually modified 
to take advantages of the state of our shared codebase that have happened 
over the last eight years.

In the beginning, this code was written at a time where I was pressed to 
have a system to install the servers that I was responsible for installing 
and configuring to perform the function request by the client.  I needed a 
system that could install preconfigured systems in a reliable and predictable 
manner.  I had become familiar with FAI, and I started using this to meet 
my needs.  During this time, I felt that using a SQL database to hold 
the smaller particulars of the installation data would come in handy, due 
to the relational nature of the database.  While inheritance and 
hierarchies can become more involved with a relational database, the format 
is handy for performing many management activities with the configuration 
can become more difficult when the configuration is stored in a filesystem.

I also wanted to exceed some of the limitations that constrained me when 
using FAI.  The manner in which FAI operates depends on an nfs mount on 
a local network.  Paella, however, only needs access to the configuration 
database.  The live system that contains the installer can be run from 
nfs, cdrom, or usb.  This allows installation on machines that are don't 
have PXE capability, as well as allowing installation of servers where the 
configuration database is not located on the local network.  Furthermore, 
I desired to develop a gui to manipulate the configuration, and the sql 
database lent itself to quicker gui development.

### Features on Older Version
- Automated network installation over a local network.

- The configuration is split into conceptual entities that are
  organized in a manner that defines a machine by the functions 
  that it performs, the group of machines it belongs to according to 
  network, role, or any other criteria that you define.

- The boot media is created from debian live, which allows for nfs,
  cdrom, and usb media types.

- A gui exists to help manage the database.

- The installer system is very flexible, where each step in the 
  configuration is able to be overridden with a script.

- The system is split into independent packages that clearly describe 
  their requirements, attempting to relieve the bloat that can occur 
  when using a single source tree to provide functionality in 
  differing environments (for example, qt4 doesn't need to be present 
  on the installation systems).

- The system can be used to install preconfigured machines that are 
  ready to be deployed to another network, or it can be used to install 
  machines on the local network as a service.  The distinction depends upon 
  the configuration of the database.

- Paella works upon the principle that the value of an entity, such as a 
  hostname, should be stored in one place, then referenced from other places 
  as the need requires, rather than being copied. (http://paella.berlios.de/docs/abstract.html#one-location-for-a-variable)

- The structure of the database allows the administrator to distinguish 
  between logical and physical configurations.  This allows the administrator 
  to more easily upgrade a machine to a new physical configuration.
