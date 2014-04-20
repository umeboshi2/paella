# [Paella](#)

## Introduction 

Paella is a system for automatically installing fully configured 
[debian](http://debian.org) machines on a local network, and managing 
their configuration.  Paella combines PXE booting, preseeded base debian 
installs, and [salt](http://saltstack.org) to install a fully configured 
system and maintain the configuration.

Paella requires quite a few things in order to operate.  The best way to 
get things started is to use [Virtual Box](http://virtualbox.org) and 
[Vagrant](http://vagrantup.com) to install and configure the Paella 
server.  The complexity of installing and configuring the network 
services, creating the debian repositories, creating and installing 
the default live system, is handled by provisioning the vagrant virtual 
machine with salt.  Instructions for using vagrant to setup paella are 
[here](#pages/vagrant)





