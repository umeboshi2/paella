# [Paella](#)


## Introduction 

Paella is a system for automatically installing fully configured 
[debian](https://debian.org) machines on a local network, and managing 
their configuration.  While the focus is on debian systems, it is currently
possible to extend paella with little development effort to install other
linux distributions that are capable of netboot installs.  In all honesty, as
long as an operating system supports netboot installs, or if it can be
installed using a [debian live](http://live.debian.net) system that is
booted over the wire or from media (possibly with the help of virtualbox or
some other tool), it can be installed with paella.  If the operating system
is capable of running a [salt-minion](https://saltstack.com) after install,
it can be configured either continuously, or as needed, with paella.  Currently,
this includes many major linux distrubutions, newer apple operating systems,
and microsoft windows systems.

While the possibilities seem numerous, the cold hard fact is that this is a
project created by a single developer to perform installation and configuration
management operations on a smaller range of operating systems and
hardware configurations.  However, I have taken the time to keep the
framework open and flexible.  The configuration management system is
actually an open and fair game.  There should not be much difficulty in
using another system such as ansible or puppet if desired.  The example
salt configuration that is provided isn't required for operation, and is also
not highly opinionated.

The machine management data is split between a postgresql database
and the configuration management system, which is currently salt.  The
postgresql database houses the minion_id/hostname and system-uuid
of the machine, as well as the disk configuration held in the form of
debian-installer expert recipes.  The decision to have this split, instead
of a centralized data store stems from the desire to keep the configuration
management system as open as possible and determine the best way
to link the information in the database to the preferred configuration
system.  I feel that this opportunity for flexibility overrides the desire for
a completely central database at this point in the development of the
project.

## Features

Paella has some features that may make it desirable over other
automated installation options.

### Self Hosting

The development environment, using [vagrant](FIXME), creates a
[virtual box](FIXME) server with two interfaces that is ready to
perform automated installs.  All that is needed is to clone the
project from [github](FIXME) and type `vagrant up` (and sadly,
followed by one `vagrant provision`, due to a small bug in the ordering
of states) and you are ready to start submitting machines and instaling.

The vagrant virtual machine can also install to bare metal if you bridge the
secondary network interface on the VM to a real network interace on the host.

### Modern Design

After spending the better part of thirteen years automatically installing and
semi-automatically maintaining configurations on quite a few debian systems,
ranging from servers to desktops and simple devices running debian, I have
learned plenty about installing debian systems, as well as a few others.

#### Debian Installer

I have learned to make use of the debian installer to perform the initial
install phase, rather than continue the tradition of debootstrapping from
a live system into a target directory on the system drive.  There are a
surprising about of small technical details that the debian installer handles,
and these details happen to change from release to release in ways that
forces more maintainence than is desired on the debootstrap install
method.

At it's heart, if you pay close attention, the debian installer is an API for
installing debian systems, controlled entirely by the preseed file and the
kernel command line.  The debian developers provide all of the implementation
details to install the system you declare in the preseed and command line.
Using the debian installer makes long term maintainence easier, at the
expense of having to keep track of the state of the machine when it
reboots (thankfully, this is only once).  FIXME - there is another page
that gives details on how the install procedure operates.

#### Configuration Management

Configuration management extends beyond a preconfigured installation.  When
the desire to create an automated installer that created fully configured
systems originated, configuration management as it is seen today was
nowhere nearly as mature.  There existed [cfengine](FIXME) and an assortment
of less complete solutions to the serious problems that lack of good
configuration managment eventually incurs.  Cfengine was written perl, which
I really don't like using.  I was forced, as many other administrators at the time,
to implement a hand-rolled solution, which, as expected, was less than completely
satisfactory, but performed well enough.

This is no longer needed.  There now exists a plethora of configuration management
options, many of them providing continuous or on demand configuration management
after the install and possible deployment to another location.  The large variety of
options now available implies that there are good, bad, and ugly options.  There
are very likely people that consider salt either on the bad or ugly side and would
like another option, especially over what can be perceived as a hand-rolled and
little tested crypto solution for communication, and for them, the configuration
system is basically open.  The only places where salt is used in the install process
is to add the apt repositories and install the minion and initial config.  This is
done in the preseed file and latecmd script.  The submission of a new machine
will also generate minion keys that are stored in the database and preseeded
to the minion during the latecmd.

#### Machine Administration

The primary goal of this project is to provide a nearly enterprise solution at a
budget price for smaller businesses and organizations that don't require the
full fledged expensive solution.  The growth of the internet, as well as the
increasing range and features of internet capable devices has created an
environment where it is becoming a greater necessity to define stricter
configurations and policies that keeps the business operating without
falling prey to the likelihood of increased problems and downtime as their
dependencies on interaction over the internet and with each other increases or
otherwise changes,

Paella includes a web application capable of administring the machines.  Currently
this is just the barebones necessity required to perform simple installations with
expert disk recipes.  Partition and RAID recipes can be edited on the web
application using the [ACE](FIXME) text editor in the browser.  The recipe editor
on the paella web application doesn't require the recipe to exist on a single line, or
to use backslash escaping to write the recipe.  The recipe can be written as a
normal multiline text file, that is later squeezed into the proper single line
when the preseed template is filled and served.

The paella web server itself has been written with an eye towards the
future.  The server is a [pyramid](FIXME) application using [cornice](FIXME) to
provide the [REST](FIXME) interface.  On the client side, in the browser,
everything is a single page application.  The client application is written in
[coffee-script](FIXME) and uses [backbone.marionette](FIXME) as well as
other good quality javascript libraries.

#### PXE/Netboot Environment

Paella combines PXE booting, preseeded base debian 
installs, and [salt](https://saltstack.com) to install a fully configured 
system and maintain the configuration.  Paella can also automatically install
[Microsoft Windows](https://microsoft.com) systems via PXE booting, however this
is currently a feature that needs much work.  Proof of concept and some
sample code is provided for the vagrant VM, but is disabled by default.

**NOTE**: It should be noted here, or somewhere else, that a pxe netboot is not
strictly required to perform an automated installation, since all that is
required is a syslinux config, preseed file, and possibly a different latecmd that
would keep the machine from continuously rebooting the debian installer.  PXE
installation is the preferred method, due to the ease of administration compared
to other methods.

As a consequence of having a netboot install environment, options that would
otherwise require the configuration of such an environment are already
available.  Diskless systems can be operated routinely.  There are also
backup/clone systems, recovery and repair systems, and also forensic or
other specialized tools that would benefit from operating without writing to
the fixed media of the host is needed.

A good example of this is that the windows installer works on a debian live
system and uses wimlib to install a [WIM](FIXME) file to an ntfs partition,
then execute virtualbox to prepare the bootloader.  While this is happening
a user of the live system can browse the web or use office tools while they
recover from a malware attack or broken hard drive.

#### System Dependencies

Although this is the last feature listed, it is by far the most important.  The selection
of code and environment that paella depends upon has been chosen very
carefully, but not by a team of people.  The selection of dependencies are crucial with
respect to predictable operation and long term management.  A system such as
paella has a heavy dependence on many system services, libraries, and
frameworks in order to perform its function.  These dependencies can generally
be categorized into two distinct types.

First, there are the system dependencies.  This may not be the best term, but
these dependencies are the selection of implmentations of the various services
that paella needs to install and configure systems.  These are things like DNS,
DHCP, TFTP, HTTP, SMB, etc.  These are dependencies that used, rather than
used or called directly by the paella python code.  I have chosed
the [ISC](FIXME) implementations
of dns and dhcp, H. Peter Alvin's tftp server, the venerable Apache webserver,
as well as Samba for implenting stable and reliable services.  While some of
these services are much more difficult to configure an operate compared to
many of the alternatives I have seen chosen for similar environments, the
alternatives either do not provide the flexibility, or they don't appear to have
as many eyes on the code, as the selections that I have made.

Second, there are the libraries that have been chosen to work with the
paella application.  These can generally be divided into two classes, python
and javascript.  This is where the selection of dependencies becomes much
more difficult.

[Variations on a Theme](http://en.wikipedia.org/wiki/Variations_on_a_Theme)

[Fugue](http://en.wikipedia.org/wiki/Fugue)

I am hoping that the two links provided above come close to describing
the many alternatives that can be chosen to perform similar functions.  This
is very difficult, and many times I have been left with no choice but to gamble.

What is alive today can become dead and unmaintained quickly.  The effects
may not be felt until a long time after, but when this happens, something
has to be fixed.  What is stable, unchanged and predictable can also be
a sign of stagnation and a forecast for eventual removal from the
debian archive could be in the next release.  While it is impossible to
predict this and keep it from happening, a careful selection of dependencies
can drastically reduce the frequency of those types of problems occurring.

While some of the system services may be hard to work with and configure, the
selection of software libraries that paella directly executes has been chosen
to be as easy to work with as possible, without circumventing important things
that may potentially affect the predictability and reliabilty of the code.

Nevertheless, there should be at least one or two dependencies that will
have to be worked with in the next two years, if history and experience are
any guide, which is why the selection process is so important, and it has
taken much of my time.



## Getting Started

Paella requires quite a few things in order to operate.  The best way to 
get things started is to use [Virtual Box](https://virtualbox.org) and 
[Vagrant](https://vagrantup.com) to install and configure the Paella 
server.  The complexity of installing and configuring the network 
services, creating the debian repositories, creating and installing 
the default live system, is handled by provisioning the vagrant virtual 
machine with salt.  Instructions for using vagrant to setup paella are 
[here](#pages/vagrant).


## Planned Usage and Development Direction

It seems to be quite often when a fully automated network installer is
considered to be necessary for an environment, there is a large farm
of very similar machines performing very similar functions.  Outside of
identifying and keeping track of the machines, they are not otherwise
treated differently.

It also seems to be that investment in time and knowledge required to
implement a fully automated network installation and configuration
management system drives the price of service considerably in order
for the developer of the system to receive an adequate return on the
investment spent.

The result of these facts seem to indicate that this type of software (or
service) is often labelled as "enterprise" quality, with a price tag attached
that exceeds the budget for many smaller businesses that are required to
keep and maintain a small computer network.  The goal of paella is to
deliver a similar service to a business that is almost big enough to require
an internal IT person, or some small businesses that have IT but need help
with system and network administration.





## Introduction 

Paella is a system for automatically installing fully configured 
[debian](https://debian.org) machines on a local network, and managing 
their configuration.  Paella combines PXE booting, preseeded base debian 
installs, and [salt](https://saltstack.com) to install a fully configured 
system and maintain the configuration.  Paella can also automatically install
[Microsoft Windows](https://microsoft.com) systems, however this
is currently a feature that needs much work.

Paella requires quite a few things in order to operate.  The best way to 
get things started is to use [Virtual Box](https://virtualbox.org) and 
[Vagrant](https://vagrantup.com) to install and configure the Paella 
server.  The complexity of installing and configuring the network 
services, creating the debian repositories, creating and installing 
the default live system, is handled by provisioning the vagrant virtual 
machine with salt.  Instructions for using vagrant to setup paella are 
[here](#pages/vagrant).

 ## Planned Usage and Development Direction

It seems to be quite often when a fully automated network installer is
considered to be necessary for an environment, there is a large farm
of very similar machines performing very similar functions.  Outside of
identifying and keeping track of the machines, they are not otherwise
treated differently.

It also seems to be that investment in time and knowledge required to
implement a fully automated network installation and configuration
management system drives the price of service considerably in order
for the developer of the system to receive an adequate return on the
investment spent.

The result of these facts seem to indicate that this type of software (or
service) is often labelled as "enterprise" quality, with a price tag attached
that exceeds the budget for many smaller businesses that are required to
keep and maintain a small computer network.  The goal of paella is to
deliver a similar service to a business that is almost big enough to require
an internal IT person, or some small businesses that have IT but need help
with system and network administration.




