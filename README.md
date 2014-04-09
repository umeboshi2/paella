.. -*- mode: markdown -*-

===========
Paella
===========

.. contents:: :backlinks: entry

Introduction 
----------------------

Paella is a system for that has been used to install preconfigured 
debian systems over a local network in a manner similar to FAI_.  The 
project started in 2004 as a set of scripts within the FAI installer than 
communicated with a PostgreSQL database to retrieve the configuration for 
the target machine.

The old website for this project is at http://paella.berlios.de

Current Features
-----------------------

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

TODO
-----------------------

- Cleanup vestigial portions of the code.

- Use SQLAlchemy for database access.

- Use MakoTemplates instead of the simple tag substitutions

- Integrate with salt to maintain configurations.

- Rewrite the user interface to work in a pyramid web framework.



History
---------------

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




