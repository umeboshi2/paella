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


tftpd-package:
  pkg.installed:
    - name: tftpd-hpa

