# -*- mode: yaml -*-

include:
  - default.pkgsets


nfs-kernel-server:
  service:
    - running
    - watch:
        - file: nfs-exports

netboot-support-packages:
  pkg.installed:
    - pkgs:
      - live-build
      - ipxe
      
    