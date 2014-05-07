# -*- mode: yaml -*-

samba-support-packages:
  pkg.installed:
    - pkgs:
      - smbclient

samba-server-package:
  pkg.installed:
    - name: samba
    - requires:
      - pkg: samba-support-packages


