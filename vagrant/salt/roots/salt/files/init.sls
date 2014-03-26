/etc/network/interfaces:
  file.managed:
    - source: salt://files/network-interfaces
    - user: root
    - group: root
    - mode: 644
