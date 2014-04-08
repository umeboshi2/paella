# -*- mode: yaml -*-

syslinux:
  pkg:
    - latest

nfs-kernel-server:
  pkg:
    - latest
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

