# -*- mode: yaml -*-

tftpd-hpa:
  pkg:
    - installed
  service:
    - running
    - require:
        - file: /var/lib/tftpboot
    - watch:
        - file: /var/lib/tftpboot

/var/lib/tftpboot:
  file.directory:
    - user: ${pillar['paella_user']}
    - group: ${pillar['paella_group']}
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

