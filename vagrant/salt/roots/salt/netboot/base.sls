# -*- mode: yaml -*-

include:
  - default


nfs-kernel-server:
  service:
    - running
    - watch:
        - file: nfs-exports

