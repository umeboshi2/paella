# -*- mode: yaml -*-
{% set pget = salt['pillar.get'] %}
{% set user = pget('paella:paella_user') %}
{% set group = pget('paella:paella_group') %}


# security updates
/srv/debrepos/security/conf:
  file.directory:
    - makedirs: True

/srv/debrepos/security/conf/updates:
  file.managed:
    - source: salt://debrepos/repos/security/updates
    - template: mako

/srv/debrepos/security/conf/live-packages:
  file.managed:
    - source: salt://debrepos/live-packages

/srv/debrepos/security/conf/distributions:
  file.managed:
    - source: salt://debrepos/repos/security/distributions
    - template: mako

local-packages-security:
  cmd.script:
    - creates: /srv/debrepos/security/conf/local-packages
    - source: salt://scripts/create-local-packages-list.sh
    - cwd: /srv/debrepos/security
    - require:
      - cmd: local-packages
      - file: /srv/debrepos/security/conf
      - file: /srv/debrepos/security/conf/updates
      - file: /srv/debrepos/security/conf/distributions
      - file: /srv/debrepos/security/conf/live-packages

security-repos-ready:
  cmd.run:
    - name: echo "security repos ready"
    - user: {{ user }}
    - group: {{ group }}
    - requires:
      - cmd: local-packages-security

update-security-repos:
  cmd.run:
    - name: reprepro -VV --noskipold update
    - unless: test -d /srv/debrepos/security/db
    - user: {{ user }}
    - group: {{ group }}
    - cwd: /srv/debrepos/security
    - requires:
      - cmd: security-repos-ready





