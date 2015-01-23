# -*- mode: yaml -*-
{% set pget = salt['pillar.get'] %}
{% set user = pget('paella:paella_user', 'vagrant') %}
{% set group = pget('paella:paella_group', 'vagrant') %}

include:
  - default.pkgsets
  - shorewall
  - iscdhcp
  - ipxe
  - samba.config
  - saltmaster
  - mainserver
  - paella-netboot.base
  - rsyslog
  
tftpd-default-config:
  file.managed:
    - name: /etc/default/tftpd-hpa
    - source: salt://paella-netboot/tftpd-default-config
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

tftpd-package:
  pkg.installed:
    - name: tftpd-hpa
      
tftpd-service:
  service.running:
    - name: tftpd-hpa
    - require:
        - file: tftpbootdir
    - watch:
        - file: tftpbootdir

nfs-incoming-share:
  file.directory:
    - name: /srv/shares/incoming
    - makedirs: True
    - mode: 777
      
nfs-exports:
  file.managed:
    - name: /etc/exports
    - source: salt://paella-netboot/nfs-exports
    - user: root
    - group: root
    - mode: 644
    - template: mako
    - require:
      - file: nfs-incoming-share

nfs-kernel-server-package:
  pkg.installed:
    - name: nfs-kernel-server
      
nfsd-service:
  service.running:
    - name: nfs-kernel-server
    - watch:
        - file: nfs-exports

