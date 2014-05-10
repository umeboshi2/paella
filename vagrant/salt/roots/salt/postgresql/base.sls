# -*- mode: yaml -*-

postgresql-support-packages:
  pkg.installed:
    - pkgs:
      - postgresql-contrib


postgresql-package:
  pkg.installed:
    - name: postgresql
    - requires:
      - pkg: postgresql-support-packages

