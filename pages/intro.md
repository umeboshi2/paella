# Introduction 

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

# Features

[Here](#pages/features) is a page of features.

# Getting Started

Paella requires quite a few things in order to operate.  The best way to 
get things started is to use [Virtual Box](http://virtualbox.org) and 
[Vagrant](https://vagrantup.com) to install and configure the Paella 
server.  The complexity of installing and configuring the network 
services, creating the debian repositories, creating and installing 
the default live system, is handled by provisioning the vagrant virtual 
machine with salt.  Instructions for using vagrant to setup paella are 
[here](#pages/vagrant).

# Development

The core of paella is written in [python](http://python.org).
[Here](#pages/pythondev) is a page with some
information about what python libraries are used with paella.  For the
web application, I have written a page discussing the [css](#pages/cssdev)
and [javascript](#pages/jsdev) environments.

# Planned Usage and Development Direction

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



