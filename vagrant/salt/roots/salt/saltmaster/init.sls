# -*- mode: yaml -*-

salt-master:
  pkg:
    - installed
  service:
    - running
    - watch:
      - file: /etc/salt/master

/etc/salt/master:
  file.managed:
    - source: salt://saltmaster/master-config
    - user: root
    - group: root
    - mode: 644
    - template: mako

/etc/salt/pki:
  file.directory:
    - require:
      - pkg: salt-master
    - user: ${pillar['paella_user']}
    - group: ${pillar['paella_group']}
    - mode: 2775
    - recurse:
      - user
      - group

/var/log/salt:
  file.directory:
    - require:
      - pkg: salt-master
    - user: root
    - group: ${pillar['paella_group']}
    - mode: 2775
    - recurse:
      - user
      - group


