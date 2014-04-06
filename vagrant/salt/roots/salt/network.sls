# -*- mode: yaml -*-


/etc/network/interfaces:
  file.managed:
    - source: salt://files/network-interfaces

enable-eth1:
  cmd.wait:
    - name: ifup eth1
    - watch:
      - file: /etc/network/interfaces
    - requires:
      - file: /etc/network/interfaces
      