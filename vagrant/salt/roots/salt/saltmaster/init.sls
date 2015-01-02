# -*- mode: yaml -*-

include:
  - saltmaster.base


salt-master:
  service:
    - running
    - watch:
      - file: /etc/salt/master
      - file: /etc/default/salt-master
    - require:
        - pkg: salt-master-package

/etc/default/salt-master:
  file.managed:
    - source: salt://saltmaster/master-init-default
    - template: mako
      
/etc/salt/master:
  file.managed:
    - source: salt://saltmaster/master-config
    - user: root
    - group: root
    - mode: 644
    - template: mako

/etc/salt:
  file.directory:
    - require:
      - pkg: salt-master
    #- user: ${pillar['paella_user']}
    - group: ${pillar['paella_group']}
    - mode: 2775

/etc/salt/pki:
  file.directory:
    - require:
      - pkg: salt-master
      - file: /etc/salt
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

# FIXME
# when running salt-master as unpriv user,
# this directory needs to be at least readable
# by salt master. Make /var/run/salt/master writable
# instead
/var/run/salt:
  file.directory:
    - require:
      - pkg: salt-master
    - user: root
    - group: ${pillar['paella_group']}
    - mode: 2775
    - recurse:
      - group
  
