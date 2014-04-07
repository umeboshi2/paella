# -*- mode: yaml -*-

reprepro:
  pkg:
    - latest

# use germinate to help build
# small partial debian repository
# capable of debootstrap
germinate:
  pkg:
    - latest


# This fake-random-source state is
# is to quickly generate gpg keys
# to sign the package repository.
# The keys made with this should 
# not be used outside the vagrant 
# environment.

# There is no more fake-random-source state.
# Instead, a pregenerated set of keys will 
# be used in the vagrant environment.

#fake-random-source:
#  pkg.latest:
#    - name: rng-tools
#  service:
#    - running
#    - name: rng-tools
#  file.managed:
#    - name: /etc/default/rng-tools
#    - source: salt://debrepos/rng-tools

/srv/debrepos/paella.gpg:
  file.managed:
    - source: salt://debrepos/paella-insecure-pub.gpg

/home/vagrant/paella-insecure-sec.gpg:
  file.managed:
    - source: salt://debrepos/paella-insecure-sec.gpg
    - user: vagrant
    - group: vagrant
    - mode: 400

/home/vagrant/wheezy-stable.gpg:
  file.managed:
    - source: salt://debrepos/wheezy-stable.gpg
    - user: vagrant
    - group: vagrant
    - mode: 644

/home/vagrant/wheezy-automatic.gpg:
  file.managed:
    - source: salt://debrepos/wheezy-automatic.gpg
    - user: vagrant
    - group: vagrant
    - mode: 644

import-insecure-gpg-key:
  cmd.run:
    - name: gpg --import paella-insecure-sec.gpg
    - unless: gpg --list-key 62804AE5
    - user: vagrant
    - group: vagrant
    - cwd: /home/vagrant
    - requires:
      - file: /home/vagrant/paella-insecure-sec.gpg

import-wheezy-automatic-key:
  cmd.run:
    - name: gpg --import wheezy-automatic.gpg
    - unless: gpg --list-key 46925553
    - user: vagrant
    - group: vagrant
    - cwd: /home/vagrant
    - requires:
      - file: /home/vagrant/wheezy-automatic.gpg


import-wheezy-stable-key:
  cmd.run:
    - name: gpg --import wheezy-stable.gpg
    - unless: gpg --list-key 65FFB764
    - user: vagrant
    - group: vagrant
    - cwd: /home/vagrant
    - requires:
      - file: /home/vagrant/wheezy-stable.gpg






/srv/debrepos/debian/conf:
  file.directory:
    - makedirs: True


i386-udeb-list-upstream:
  file.managed:
    - name: /srv/debrepos/debian/conf/i386-udeb-list-upstream
    - source: http://ftp.us.debian.org/debian/dists/wheezy/main/installer-i386/current/images/udeb.list
    - source_hash: sha256=15ce82c5c843a4d752932e05596a3ae22d7575e4b713a27a4367a7d2697a5777


cat /srv/debrepos/debian/conf/i386-udeb-list-upstream | awk '{print $1 "\tinstall"}' > /srv/debrepos/debian/conf/i386-udeb-list:
  cmd.run:
    - requires:
        - file: i386-udeb-list-upstream
    - creates: /srv/debrepos/debian/conf/i386-udeb-list


/srv/debrepos/debian/conf/live-packages:
  file.managed:
    - source: salt://debrepos/live-packages

/srv/debrepos/debian/conf/updates:
  file.managed:
    - source: salt://debrepos/updates

/srv/debrepos/debian/conf/distributions:
  file.managed:
    - source: salt://debrepos/distributions

include:
  - apache
  - tftpd
  - bind
  - dhcpd
  - shorewall
  - squid
  - debianlive
  - netboot



local-packages:
  cmd.run:
    - creates: /srv/debrepos/debian/conf/local-packages
    - name: dpkg --get-selections > /srv/debrepos/debian/conf/local-packages
    - require:
      - sls: apache
      - sls: tftpd
      - sls: bind
      - sls: dhcpd
      - sls: shorewall
      - sls: debianlive
      - sls: netboot
      - pkg: squid


/usr/local/bin/make-master-pkglist:
  file.managed:
    - source: salt://scripts/make-master-pkglist.py
    - mode: 755
    - requires: local-packages



