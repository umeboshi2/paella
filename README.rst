.. -*- mode: rst -*-

===========
Abstract
===========

.. contents:: :backlinks: entry

Introduction 
----------------------

Paella is system for creating/installing customized debian systems.
There are no current plans for configuration updates on live systems,
that's not it's initial purpose, although it may be extended later.

Paella differs from other automated installation system by using a 
PostgreSQL database to store all of the configuration.  PostgreSQL was 
chosen primarily because it supports foreign keys and stored procedures.  
Foreign keys are used to keep the relationships in the configuation tied 
together, and this can be useful for maintaining a configuation over a long 
time as it helps to keep it from breaking due to broken relationships between 
the different parts of the configuration.  This doesn't make it impossible to 
make a broken configuration, or to break a good configuration, but it does 
help quite a bit.  It also helps organize the configuration so that it is easier to 
tell what is going to be installed and configured.




Inspiration
--------------------

Inspiration for paella comes from many places.  Since inspiration is 
what it is, please note that the following sections were written quite a few 
years ago.  While the inspiration hasn't really changed much, the focus of 
development has changed to match and make use of the improvements 
and additions that have occured in the software community since paella 
was started.


FAI
!!!!!!!!!!!!!!!

FAI (the fully automated installer)
An excellent installer, with the capability of bootstrapping
an entire network!  paella was going to just complement fai,
but I'm starting to prefer the configuration layout i'm planning,
so paella will probably completely replace fai.  

Much of this has been done, and now only the setup-storage 
command is being used from the fai-client package.  There is 
no need to reinvent the wheel here, as setting up disks can 
be complex and error proned if it's not managed right.

Debconf
!!!!!!!!!!!!!!!!!!!

Debconf is an important abstract configuration system.

Much of the inspiration for paella comes straight from both 
debconf and FAI.  I wanted to make a system that held the 
configuration for many packages in many formats and be 
able to use an automated installer to install the configuration 
onto systems.  Also, I wanted to keep the management of 
the configuration separate from the system it was being 
installed to, to keep the system from depending on paella.

Knoppix 
!!!!!!!!!!!!!!!!!!!!!!

,,, and Morphix, Gnoppix, and other live cd's

Debian Live has made most of the live cd's obsolete, and it's 
now the preferred method of creating a live system.  It's 
planned to be able to use paella to generate the chroot directory 
then use debian live to build the binary image.  This has been
done, and it is fairly simple.  The basic method of doing this is 
performed in the quickstart_ guide.  Since debian live can 
make live systems on many media types, including network 
images, it's now being used for the paella installer.


Demudi, Debian-Lex, ...
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

I think paella can be very instrumental in helping configure and
install a custom network on a per network type basis, (i.e. what
machines are on the network and what are there jobs, expected
activities, etc.  I am also thinking of networks with custom configured
roaming pda's, laptops, or whatever can take a debian system.

The paragraph above was written long ago, and now there are 
custom debian distribution packages that help make this easier.  
I think that paella could still be useful here, but I have not really 
looked at the cdd package very much.  Much of the reason for 
paella's existence is to make it easier to make machines that 
are configured to perform special sets of tasks.


Design Principles
-------------------------------

Believe it or not, there was some thought behind how a configuration for 
a newly installed machine should be structured.  I have been guided by 
ideas that I like, and also by some ideas that I didn't like.  I have tried to 
express those ideas, the best I could, into the design of paella.  Due to 
time constraints, and effort required to implement some of those ideas, 
I couldn't effectively express some of them, but I have focused on the 
ideas that I felt were the most important.

One Location for a Variable
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

One of the most tiresome activities in setting up a new system is the 
repetition of some parts of the configuration.  This is probably most 
evident when entering ip addresses, netmasks, and similar info into 
the many configuration files that a system has.  I have designed paella 
to keep this repetition down to a minimum.  Theoretically, there should 
be only one place where a variable should reside, and anything needing 
the value of that variable would retrieve it from that one place.  I have 
come very close to accomplishing this, with only a few exceptions (and 
most of those exceptions are due to being in a hurry, not from any 
technical limitations).

Let's look at an example, using hostnames.  I will use the part of the 
localnet trait to demonstrate.  Suppose you are installing a server 
for a small business, and it's a hard sell, so you can only sell one 
server.  For starters, you make this server a firewall/router/fileserver.  
Let's look a sampling of the variables::

      global:hostname = strawberry
      localnet:mainserver = <--|global:hostname|-->
      localnet:file_server = <--|localnet:mainserver|-->
      localnet:samba_server = <--|localnet:file_server|-->
      localnet:nfs_server = <--|localnet:file_server|-->

Now imagine a similar place with two servers, one acting as the 
firewall/router, and another acting as the file server::

      localnet:mainserver = strawberry
      localnet:file_server = mango
      localnet:samba_server = <--|localnet:file_server|-->
      localnet:nfs_server = <--|localnet:file_server|-->

      strawberry global:hostname = <--|localnet:mainserver|-->
      mango global:hostname = <--|localnet:file_server|-->

Actually setting the configuration is a bit more involved than this, as 
I have neglected to mention dns, dhcp, and other things, but I merely 
want to illustrate a point.  The localnet variables would be in a family, 
and that family would be attached to the mango and strawberry 
machines.  The global:hostname variables would be attached to each 
machine.  Using the variables this way also helps to keep the purpose 
of the variable known, as we can see that the hostname for mango is 
set to the fileserver for the local network.

(The databases that ship with paella are only examples.  Feel free to 
make a configuration that makes more sense to you.  I have tried to 
make paella very flexible.)

		 

Separation of the Logical System and the Physical System
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

I have tried to structure the objects in the paella database to make it 
easy to distinguish from a logical system that performs it jobs, and 
the machine where it is installed.  I haven't made anything that actually 
enforces the separation, so it is up to the administrator to decide what 
belongs to a logical system, and what belongs to a physical system.  

Here is a quick rundown:

+ **Traits**: Traits are the smallest component indicating a "feature".  They can be 
  either logical, physical, or both.  The variables used in a trait can be physical or 
  logical, and you would use families to divide them.

+ **Profiles**:  Profiles are the ordered collection of traits to be installed, and the 
  famillies of configuration values that will be applied to it.  This is meant to 
  represent a logical system, so you can install a profile to different machines.

+ **Families**:  Families are a collection of variables.  They can be physical or 
  logical, but they shouldn't be both.  You attach logical families to a profile, and 
  physical families to a machine.

+ **Machines**:  Machines are meant to represent the physical host that a profile 
  will be installed on.  The variables for a machine should be physical.

The use of the terms "logical" and "physical" are made generally, and aren't 
to be taken too literally.  For example, I usually attach the hostname variable 
to a machine, although it's not as "physical" as a mac address, or video 
driver.  The idea behind this is to separate the variables that can be used on 
any machine, from the variables that are only useful to one machine, or a 
set of machines.


toc_

.. _toc: index.html
.. _quickstart: quickstart-vbox.html


