# -*- mode: yaml -*-

syslinux:
  pkg:
    - latest

nfs-kernel-server:
  pkg:
    - latest


/var/cache/netboot/netboot-i386.tar.gz:
  file.managed:
    - source: http://ftp.nl.debian.org/debian/dists/wheezy/main/installer-i386/current/images/netboot/netboot.tar.gz
    - source_hash: sha256=feb4b1164e3c0bf51ecaa11649e9d9d80f17fce314178afbd8680abada9a17d4

/var/cache/netboot/netboot-amd64.tar.gz:
  file.managed:
    - source: http://ftp.nl.debian.org/debian/dists/wheezy/main/installer-amd64/current/images/netboot/netboot.tar.gz
    - source_hash: sha256=453df75cfc1b81f88bd2f2796c25ed94c45510272d034a77327ebfba1161497c

/var/cache/netboot/livebuild:
  file.directory:
    - user: root
    - group: root
    - require: 
      - file: /var/cache/netboot/netboot-i386.tar.gz
      - file: /var/cache/netboot/netboot-amd64.tar.gz

install-netboot:
  cmd.script:
    - require: 
      - file: /var/cache/netboot/netboot-i386.tar.gz
      - file: /var/cache/netboot/netboot-amd64.tar.gz
      - file: /var/lib/tftpboot
    - source: salt://scripts/install-netboot.sh
    - user: root
    - group: root
    - shell: /bin/bash

