# -*- mode: yaml -*-

salt-master:
  pkg:
    - installed
  service:
    - running

/etc/salt/pki:
  file.directory:
    - require:
      - pkg: salt-master
    - user: vagrant
    - group: vagrant
    - mode: 2775
    - recurse:
      - user
      - group

/var/log/salt:
  file.directory:
    - require:
      - pkg: salt-master
    - user: root
    - group: vagrant
    - mode: 2775
    - recurse:
      - user
      - group


/etc/salt/master:
  file.managed:
    - source: salt://saltmaster/master-config
    - user: root
    - group: root
    - mode: 644

