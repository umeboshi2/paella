# [Paella](#)

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

## Windows

Paella has the ability to install Microsoft Windows 7 over the network.  Evaluation
[iso images](http://answers.microsoft.com/en-us/windows/forum/windows_7-windows_install/cannot-find-digital-river-download-site/66a8439b-0d16-4b70-92f7-1c8486a46ebf) can be obtained to help with development.  In the development environment,
an evaluation iso for both i386 and amd64 are mounted loopback on the server and
served through samba.  A special iso is created on the server using
[wimlib](http://wimlib.sourceforge.net/) that contains a script to
mount the samba share and start an unattended install.

Automated installations of windows have been inspired by
[unattended](http://unattended.sourceforge.net/).  The ability to
install and configure a windows system in a manner similar to FAI or paella
is appealing, however the length of time and excessive rebooting required
by windows makes it infeasible to automate installs in this manner.  Instead,
a middle road will be taken by working to automate the creation of
reference images that can be automatically installed with paella.

The installation of a reference image over the network is rather interesting.  The
debian-live system partitions the disk and creates an NTFS filesystem, then uses
wimlib-imagex to install the image to the filesystem.  After this, a
[virtualbox](https://virtualbox.org) VM is created and the physical
hard drive on the machine is attached to it.  The VM then boots from an iso
that runs a script to configure the boot manager.  The windows machine is
completely installed and ready to boot without having to leave the
debian-live system!  The simple script that does this can be viewed
[here](https://github.com/umeboshi2/paella/blob/master/vagrant/salt/roots/salt/debianlive/install-win7-image.sh).










