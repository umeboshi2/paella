isc-dhcp-server:
  pkg:
    - latest

/etc/dhcp/dhcpd.conf:
  file.managed:
    - source: salt://dhcpd/files/dhcpd.conf
    - user: root
    - group: root
    - mode: 644

