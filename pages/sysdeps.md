# System Dependencies

## Short List

- [Vagrant](https://vagrantup.com)

- [VirtualBox](http://virtualbox.org)

- [Debian Installer](https://www.debian.org/devel/debian-installer/)

- [Salt](http://github.com/saltstack/salt.git)

- [wimlib](http://wimlib.sourceforge.net/) - optional

- [ISC Bind and DHCPD](http://isc.org/)

- [tftp-hpa](https://www.kernel.org/pub/software/network/tftp/)

- [Samba](http://samba.org)

- [Apache](http://apache.org)



First, there are the system dependencies.  This may not be the best term, but
these dependencies are the selection of implmentations of the various services
that paella needs to install and configure systems.  These are things like DNS,
DHCP, TFTP, HTTP, SMB, etc.  These are dependencies that used, rather than
used or called directly by the paella python code.  I have chosed
the [ISC](http://isc.org/) implementations
of dns and dhcp, H. Peter Anvin's tftp server, the venerable Apache webserver,
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

## CSS

[cssdev](#pages/cssdev)

## JS

[jsdev](#pages/jsdev)
