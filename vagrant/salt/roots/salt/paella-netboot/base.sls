# -*- mode: yaml -*-

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
      
nfs-kernel-server:
  service:
    - running
    - watch:
      - file: nfs-exports
    - require:
      - pkg: nfs-kernel-server-package
        
netboot-support-packages:
  pkg.installed:
    - pkgs:
      - live-build
      - ipxe
      - syslinux
      - cdebootstrap
      # FIXME: this breaks wheezy
      # make macro to generate netboot
      # package names
      - debian-installer-8-netboot-amd64
      