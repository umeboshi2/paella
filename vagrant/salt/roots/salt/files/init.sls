/etc/network/interfaces:
  file.managed:
    - source: salt://files/network-interfaces
    - user: root
    - group: root
    - mode: 644

/usr/local/bin/install-netboot:
  file.managed:
    - source: salt://files/install-netboot.sh
    - user: root
    - group: root
    - mode: 755
    - require: 
        - file: /var/cache/netboot/netboot.tar.gz
  cmd.run:
    - name: /usr/local/bin/install-netboot
