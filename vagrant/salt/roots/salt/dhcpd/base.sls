# -*- mode: yaml -*-

isc-dhcp-server-package:
  pkg.installed:
    - name: isc-dhcp-server

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