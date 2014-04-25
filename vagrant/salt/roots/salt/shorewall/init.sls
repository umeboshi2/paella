# -*- mode: yaml -*-

    
include:
  - network
  - shorewall.macros

shorewall:
  pkg:
    - installed

restart-shorewall:
  cmd.run:
    - name: /etc/init.d/shorewall restart
    - unless: shorewall status
    - requires:
      - pkg: shorewall
      - file: /etc/shorewall/interfaces
      - file: /etc/shorewall/Makefile
      - file: /etc/shorewall/masq
      - file: /etc/shorewall/policy
      - file: /etc/shorewall/routestopped
      - file: /etc/shorewall/rules
      - file: /etc/shorewall/zones
      - file: /etc/default/shorewall
      - sls: network

/etc/shorewall/interfaces:
  file.managed:
    - source: salt://shorewall/templates/double/interfaces
    - user: root
    - group: root
    - mode: 644

/etc/shorewall/Makefile:
  file.managed:
    - source: salt://shorewall/templates/double/Makefile
    - user: root
    - group: root
    - mode: 644

/etc/shorewall/masq:
  file.managed:
    - source: salt://shorewall/templates/double/masq
    - user: root
    - group: root
    - mode: 644

/etc/shorewall/policy:
  file.managed:
    - source: salt://shorewall/templates/double/policy
    - user: root
    - group: root
    - mode: 644

/etc/shorewall/routestopped:
  file.managed:
    - source: salt://shorewall/templates/double/routestopped
    - user: root
    - group: root
    - mode: 644

/etc/shorewall/rules:
  file.managed:
    - source: salt://shorewall/templates/double/rules
    - user: root
    - group: root
    - mode: 644

/etc/shorewall/shorewall.conf:
  file.managed:
    - source: salt://shorewall/templates/double/shorewall.conf
    - user: root
    - group: root
    - mode: 644

/etc/shorewall/zones:
  file.managed:
    - source: salt://shorewall/templates/double/zones
    - user: root
    - group: root
    - mode: 644

/etc/default/shorewall:
  file.managed:
    - source: salt://shorewall/templates/default
    - user: root
    - group: root
    - mode: 644




