# -*- mode: yaml -*-

isc-dhcp-server:
  pkg:
    - latest
  service:
    - running
    - require:
        - file: /etc/dhcp/dhcpd.conf
        - file: /etc/default/isc-dhcp-server
        - file: /etc/network/interfaces

/etc/dhcp/dhcpd.conf:
  file.managed:
    - source: salt://dhcpd/files/dhcpd.conf
    - user: root
    - group: root
    - mode: 644

/etc/default/isc-dhcp-server:
  file.managed:
    - source: salt://dhcpd/files/default
    - user: root
    - group: root
    - mode: 644
