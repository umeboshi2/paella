# -*- mode: yaml -*-

    
include:
  - network
  - shorewall.base
  - shorewall.macros

# FIXME
# Shorewall is not a normal service, such as a running daemon, but
# a collection of iptable rules that is loaded in the kernel.  Currently,
# it seems the vagrant machine must be rebooted, or shorewall restarted
# before things work right.  
restart-shorewall:
  cmd.run:
    - name: /etc/init.d/shorewall restart
    - unless: shorewall status
    - requires:
      - pkg: shorewall-package
      - file: /etc/shorewall/interfaces
      - file: /etc/shorewall/Makefile
      - file: /etc/shorewall/masq
      - file: /etc/shorewall/policy
      - file: /etc/shorewall/routestopped
      - file: /etc/shorewall/rules
      - file: /etc/shorewall/zones
      - file: /etc/default/shorewall
      - sls: network

{% set conffiles = ['interfaces', 'Makefile', 'masq', 'policy', 'routestopped', 'rules', 'shorewall.conf', 'zones'] %}

{% for filename in conffiles: %}
/etc/shorewall/{{ filename }}:
  file.managed:
    - source: salt://shorewall/templates/double/{{ filename }}
    - user: root
    - group: root
    - mode: 644
{% endfor %}

/etc/default/shorewall:
  file.managed:
    - source: salt://shorewall/templates/default
    - user: root
    - group: root
    - mode: 644





