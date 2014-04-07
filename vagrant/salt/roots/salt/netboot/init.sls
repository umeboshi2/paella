# -*- mode: yaml -*-


/var/lib/tftpboot/installer:
  file.directory:
    - makedirs: True

/var/lib/tftpboot/installer/i386/initrd.gz:
  file.managed:
    - source: http://ftp.nl.debian.org/debian/dists/wheezy/main/installer-i386/20130613+deb7u1+b2/images/netboot/debian-installer/i386/initrd.gz
    - source_hash: sha256=ec9cd8f2f4113b6cea59165672e9a41f676ce1fe47643d8a57933d672245bd93

/var/lib/tftpboot/installer/i386/linux:
  file.managed:
    - source: http://ftp.nl.debian.org/debian/dists/wheezy/main/installer-i386/20130613+deb7u1+b2/images/netboot/debian-installer/i386/linux
    - source_hash: sha256=b60550692a0528b856f2dac883e79ec8388d392413a0954873c31f89172e0a59


/var/cache/netboot/livebuild:
  file.directory:
    - user: root
    - group: root
    - makedirs: True

include:
  - debrepos

install-netboot:
  cmd.script:
    - require:
      - file: /var/lib/tftpboot
      - sls: debrepos
    - source: salt://scripts/install-netboot.sh
    - user: root
    - group: root
    - shell: /bin/bash

