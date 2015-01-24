# [Paella](#)


## History

The old website for this project is at http://paella.berlios.de

**This page needs to be rewritten/reorganized**

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
point in time, many of the upstream sources that paella depends upon have 
all been largely abandoned by world developers at large, in favor of sources 
that are being actively developed and maintained.  This effectively puts the 
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

- The boot media is created from debian live, which allows for netboot,
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



## That was then, this is now

Paella is not a new project.  It has been rewritten entirely from scratch.
You are looking at what could best be called version 2.  A brief overview
of version 1, and the inspiration for paella and some of what it did is on
the ["history page"](#page/history).

Configuration management never made it past install.  Using paella (v1)
to keep and maintain a configuration would require some sort of state
management that was more easily presumed with a fresh install, than
could be easily done after deployment.  This required to much time and
attention in the past when good configuration management systems were
few and far between.  My dislike for [PERL](http://perl.com) kept me from
contributing to [FAI](https://fai-project.org) as well as using cfengine.
I briefly looked into using bcfg2, but couldn't quite get it working
to my satisfaction.

At sometime, when paella v1 was showing its age,
[puppet](https://puppetlabs.com) was
becoming quite popular.  Puppet became popular enough to seem to inspire
other configuration management systems.  This lead me to look again for another
configuration management system that was based upon python.  There were a
few systems to choose from, but the choice was between
[ansible](https://ansible.com) and [salt](https://saltstack.com).  I wound
up using salt, primarily for the use of [zeromq](https://zeromq.org) for
communication.

## Paella and FAI

Paella was originally inspired by [FAI](https://fai-project.org), and in fact,
the earliest incarnation was a set of python scripts that communicated with
a [postgresql](https://postgresql.org) database.  Much of the manner in
which paella operated was in many ways similar to FAI, especially the ability to
hook into and modify each part of the installation process.  The desire to create
a project similar to FAI, rather than contribute, was honestly based upon a
strong preference for using [python](https://python.org) instead of
[perl](https://perl.com) for development.

Unlike, FAI, paella is no longer using the [debian-live](https://live.debian.net/)
to install the debian systems.  Instead, the
[debian installer](https://www.debian.org/devel/debian-installer/) is being
used to [install](#pages/debian-install) the base system
and prepare it to be configured with salt on the
next reboot.  Up until the present rewrite, paella depended upon 
[fai-setup-storage](https://packages.debian.org/unstable/main/fai-setup-storage),
which was thoughtfully split from the other FAI packages, as it proves to be
very useful.  There exists a possibility that fai-setup-storage may be included
along with febootstrap to automatically install rpm type systems.

Also, paella uses a [web server](#pages/paella-server) to help with the installation and
management of the machines.  While the browser application is still in it's
infancy and only performs the most minimal of management functions, the
api it provides allows the debian installs to retrieve preseed files and special
scripts that are specific to each machine.  The setup is used to inform the
paella server when debian install is completed on each machine, deconfiguring
the specific PXE configuration file that booted the machine and providing for
further configuration with salt upon reboot.

