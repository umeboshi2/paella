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

(This hasn't been tested on windows)

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
