# -*- mode: yaml -*-

tftpd-hpa:
  pkg:
    - latest
  service:
    - running
    - require:
        - file: /var/lib/tftpboot

/var/lib/tftpboot:
  file.directory:
    - user: vagrant
    - group: vagrant
    - dir_mode: 755
    - file_mode: 644
    - makedirs: True
    - recurse:
        - user
        - group
        - mode

/etc/default/tftpd-hpa:
  file.managed:
    - source: salt://tftpd/files/default
    - user: root
    - group: root
    - mode: 644

