# -*- mode: yaml -*-

include:
  - dhcpd.base

isc-dhcp-server:
  service:
    - running
    - require:
        - pkg: isc-dhcp-server-package
        - file: /etc/dhcp/dhcpd.conf
        - file: /etc/default/isc-dhcp-server
        - file: /etc/network/interfaces
        - cmd: enable-eth1
    - watch:
        - file: /etc/dhcp/dhcpd.conf
        - file: /etc/default/isc-dhcp-server
        - file: /etc/network/interfaces


