# -*- mode: yaml -*-

include:
  - schroot.base


bootstrap_wheezy_i386_chroot:
  cmd.run:
    - name: debootstrap --arch=i386 --keyring=/home/vagrant/.gnupg/pubring.gpg --variant=buildd --include=devscripts,pkg-config,autoconf,automake,libtool,debhelper,autotools-dev,libfuse-dev,libselinux1-dev,libxml2-dev,libssl-dev,ntfs-3g-dev,libattr1-dev,attr wheezy /srv/roots/wheezy-i386 file:///srv/debrepos/debian
    - unless: test -r /srv/roots/wheezy-i386/bin/bash
    - require:
        - pkg: schroot-packages
        - file: schroot-parent-directory
        - file: schroot.conf

