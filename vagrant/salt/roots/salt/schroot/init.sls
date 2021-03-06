# -*- mode: yaml -*-

include:
  - default.pkgsets
  - schroot.base
  
{% for dist in ['wheezy', 'jessie']: %}
{% for arch in ['amd64', 'i386']: %}
{% set builddeps = 'devscripts,fakeroot,pkg-config,autoconf,automake,libtool,debhelper,autotools-dev,libfuse-dev,libselinux1-dev,libxml2-dev,libssl-dev,ntfs-3g-dev,libattr1-dev,attr' %}
bootstrap_{{ dist }}_{{ arch }}_chroot:
  cmd.run:
    - name: debootstrap --arch={{ arch }} --keyring=/home/vagrant/.gnupg/pubring.gpg --variant=buildd --include={{ builddeps }} {{ dist }} /srv/roots/{{ dist }}-{{ arch }} file:///srv/debrepos/debian
    - unless: test -r /srv/roots/{{ dist }}-{{ arch }}/bin/bash
    - require:
      - pkg: schroot-packages
      - file: schroot-parent-directory
      - file: schroot.conf
{% endfor %}
{% endfor %}

# The schroot package is used to build packages.
# Currently, an i386 chroot is used to build the wimlib package
# for i386.  The amd64 version is built on normal root.

# FIXME, find dependency path and mark it better.  When is this
# state called?  How are we sure local debrepos exists?
#bootstrap_wheezy_i386_chroot:
#  cmd.run:
#    - name: debootstrap --arch=i386 --keyring=/home/vagrant/.gnupg/pubring.gpg --variant=buildd --include=devscripts,fakeroot,pkg-config,autoconf,automake,libtool,debhelper,autotools-dev,libfuse-dev,libselinux1-dev,libxml2-dev,libssl-dev,ntfs-3g-dev,libattr1-dev,attr wheezy /srv/roots/wheezy-i386 file:///srv/debrepos/debian
#    - unless: test -r /srv/roots/wheezy-i386/bin/bash
#    - require:
#        - pkg: schroot-packages
#        - file: schroot-parent-directory
#        - file: schroot.conf

