# -*- mode: yaml -*-
{% set pget = salt['pillar.get'] %}
{% set user = pget('paella_user') %}
{% set group = pget('paella_group') %}

include:
  - default
  - shorewall
  - dhcpd
  - samba
  - saltmaster
  - mainserver
  - netboot.base

tftpd-default-config:
  file.managed:
    - name: /etc/default/tftpd-hpa
    - source: salt://netboot/tftpd-default-config
    - user: root
    - group: root
    - mode: 644

tftpbootdir:
  file.directory:
    - name: /var/lib/tftpboot
    - user: {{ user }}
    - group: {{ group }}
    - dir_mode: 755
    - file_mode: 644
    - makedirs: True
    - recurse:
        - user
        - group
        - mode

tftpd-service:
  service.running:
    - name: tftpd-hpa
    - require:
        - file: tftpbootdir
    - watch:
        - file: tftpbootdir

nfs-exports:
  file.managed:
    - name: /etc/exports
    - source: salt://netboot/nfs-exports
    - user: root
    - group: root
    - mode: 644
    - template: mako

nfsd-service:
  service.running:
    - name: nfs-kernel-server
    - watch:
        - file: nfs-exports

