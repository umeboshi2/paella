# -*- mode: yaml -*-

# These state are here to make sure the secondary network
# interface on the vagrant machine is properly configured.
# This allows installs to other virtual machines, or bare-metal
# machines if the secondary interface is bridged to a real
# interface.

/etc/network/interfaces:
  file.managed:
    - source: salt://network/network-interfaces
    - template: mako

enable-eth1:
  cmd.wait:
    - name: ifup eth1
    - watch:
      - file: /etc/network/interfaces
    - requires:
      - file: /etc/network/interfaces
      
