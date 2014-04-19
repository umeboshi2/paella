# -*- mode: yaml -*-

isc-dhcp-server:
  pkg:
    - installed
  service:
    - running
    - require:
        - file: /etc/dhcp/dhcpd.conf
        - file: /etc/default/isc-dhcp-server
        - file: /etc/network/interfaces
        - cmd: enable-eth1

        


/etc/dhcp/dhcpd.conf:
  file.managed:
    - source: salt://dhcpd/files/dhcpd.conf
    - user: root
    - group: root
    - mode: 644
    - template: mako

/etc/default/isc-dhcp-server:
  file.managed:
    - source: salt://dhcpd/files/default
    - user: root
    - group: root
    - mode: 644
