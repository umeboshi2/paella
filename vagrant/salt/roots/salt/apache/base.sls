# -*- mode: yaml -*-

apache-support-packages:
  pkg.installed:
    - pkgs:
      - libapache2-mod-wsgi
      - apache2-mpm-worker
      - apache2-utils


apache-package:
  pkg.installed:
    - name: apache2
    - requires:
      - pkg: apache-support-packages

