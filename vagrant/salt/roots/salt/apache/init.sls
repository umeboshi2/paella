# -*- mode: yaml -*-

include:
  - apache.base

/var/www/index.html:
  file.managed:
    - source: salt://apache/index.html


/etc/apache2/conf.d/debrepos:
  file.managed:
    - source: salt://apache/debrepos.conf
    - template: mako

apache-service:
  service.running:
    - name: apache2
    - require:
      - pkg: apache-package
    - watch:
      - file: /etc/apache2/conf.d/debrepos
    

