# -*- mode: yaml -*-

apache-support-packages:
  pkg.installed:
    - pkgs:
      - libapache2-mod-wsgi
      - apache2-mpm-worker
      - apache2-utils

apache2:
  pkg.installed:
    - name: apache2
    - requires:
      - pkg: apache-support-packages

  service:
    - name: apache2
    - running

  

/etc/apache2/conf.d/debrepos:
  file.managed:
    - source: salt://apache/debrepos.conf

