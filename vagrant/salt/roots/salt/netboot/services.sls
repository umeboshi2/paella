# -*- mode: yaml -*-

include:
  - default
  - shorewall
  - tftpd
  - dhcpd
  - samba
  - saltmaster
  - mainserver
  - netboot.base

tftpd-service:
  service.running:
    - require:
        - file: tftpbootdir
    - watch:
        - file: tftpbootdir

tftpbootdir:
  file.directory:
    - name: /var/lib/tftpboot
    - group: ${pillar['paella_group']}
    - dir_mode: 755
    - file_mode: 644
    - makedirs: True
    - recurse:
        - user
        - group
        - mode

/etc/default/tftpd-hpa:
  file.managed:
    - source: salt://netboot/tftpd-default-config
    - user: root
    - group: root
    - mode: 644

nfsd-service:
  service.running:
    - watch:
        - file: nfs-exports

nfs-exports:
  file.managed:
    - name: /etc/exports
    - source: salt://netboot/nfs-exports
    - user: root
    - group: root
    - mode: 644
    - template: mako

