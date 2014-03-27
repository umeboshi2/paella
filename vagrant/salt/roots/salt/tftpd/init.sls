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

/var/cache/netboot/netboot.tar.gz:
  file.managed:
    - source: http://ftp.nl.debian.org/debian/dists/wheezy/main/installer-i386/current/images/netboot/netboot.tar.gz
    - source_hash: sha256=feb4b1164e3c0bf51ecaa11649e9d9d80f17fce314178afbd8680abada9a17d4
