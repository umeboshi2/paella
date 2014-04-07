# -*- mode: yaml -*-

apache2:
  pkg:
    - latest
  service:
    - running

/etc/apache2/conf.d/debrepos:
  file.managed:
    - source: salt://apache/debrepos.conf

