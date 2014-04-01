# -*- mode: yaml -*-

tftpd-hpa:
  pkg:
    - latest
  service:
    - running
    - require:
        - file: /var/lib/tftpboot

syslinux:
  pkg:
    - latest

/var/lib/tftpboot:
  file.directory:
    - user: vagrant
    - group: vagrant
    - dir_mode: 755
    - file_mode: 644
    - makedirs: True
    - recurse:
        - user
        - group
        - mode

/etc/default/tftpd-hpa:
  file.managed:
    - source: salt://tftpd/files/default
    - user: root
    - group: root
    - mode: 644

/var/cache/netboot/netboot-i386.tar.gz:
  file.managed:
    - source: http://ftp.nl.debian.org/debian/dists/wheezy/main/installer-i386/current/images/netboot/netboot.tar.gz
    - source_hash: sha256=feb4b1164e3c0bf51ecaa11649e9d9d80f17fce314178afbd8680abada9a17d4

/var/cache/netboot/netboot-amd64.tar.gz:
  file.managed:
    - source: http://ftp.nl.debian.org/debian/dists/wheezy/main/installer-amd64/current/images/netboot/netboot.tar.gz
    - source_hash: sha256=453df75cfc1b81f88bd2f2796c25ed94c45510272d034a77327ebfba1161497c


