# [Paella](#)

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


