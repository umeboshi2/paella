# -*- mode: yaml -*-

syslinux:
  pkg:
    - installed

nfs-kernel-server:
  pkg:
    - installed
  service:
    - running
    - watch:
        - file: nfs-exports


nfs-exports:
  file.managed:
    - name: /etc/exports
    - source: salt://netboot-base/nfs-exports
    - user: root
    - group: root
    - mode: 644

