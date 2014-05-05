# -*- mode: yaml -*-

include:
  - default


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
    - source: salt://netboot/nfs-exports
    - user: root
    - group: root
    - mode: 644
    - template: mako

