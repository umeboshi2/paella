# -*- mode: yaml -*-

/etc/network/interfaces:
  file.managed:
    - source: salt://files/network-interfaces
    - user: root
    - group: root
    - mode: 644

install-netboot:
  cmd.script:
    - require: 
      - file: /var/cache/netboot/netboot-i386.tar.gz
      - file: /var/cache/netboot/netboot-amd64.tar.gz
      - file: /var/lib/tftpboot
    - source: salt://files/install-netboot.sh
    - user: root
    - group: root
    - shell: /bin/bash


/usr/local/bin/install-netboot:
  file.absent
