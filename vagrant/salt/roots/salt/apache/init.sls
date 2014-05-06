# -*- mode: yaml -*-

apache-support-packages:
  pkg.installed:
    - pkgs:
      - libapache2-mod-wsgi
      - apache2-mpm-worker
      - apache2-utils

/etc/apache2/conf.d/debrepos:
  file.managed:
    - source: salt://apache/debrepos.conf
    - template: mako

/etc/apache2/conf.d/paella:
  file.managed:
    - source: salt://apache/paella.conf


/etc/apache2/paella.wsgi:
  file.managed:
    - source: salt://apache/paella.wsgi
    - user: root
    - group: root
    - mode: 755

/var/www/index.html:
  file.managed:
    - source: salt://apache/index.html

apache2:
  pkg.installed:
    - name: apache2
    - requires:
      - pkg: apache-support-packages

  service:
    - name: apache2
    - running
    - watch:
      - file: /etc/apache2/paella.wsgi
      - file: /etc/apache2/conf.d/debrepos
      - file: /etc/apache2/conf.d/paella
  

