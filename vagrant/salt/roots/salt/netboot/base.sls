# -*- mode: yaml -*-

include:
  - default.pkgsets


nfs-kernel-server:
  service:
    - running
    - watch:
        - file: nfs-exports

