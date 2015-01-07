# -*- mode: yaml -*-
{% set pget = salt['pillar.get'] %}
{% set user = pget('paella:paella_user', 'vagrant') %}
{% set group = pget('paella:paella_group', 'vagrant') %}


/srv/debrepos/ubuntu/conf:
  file.directory:
    - makedirs: True

      
/srv/debrepos/ubuntu/conf/updates:
  file.managed:
    - source: salt://debrepos/repos/ubuntu/updates
    - template: mako

/srv/debrepos/ubuntu/conf/live-packages:
  file.managed:
    - source: salt://debrepos/live-packages

/srv/debrepos/ubuntu/conf/distributions:
  file.managed:
    - source: salt://debrepos/repos/ubuntu/distributions
    - template: mako

local-packages-ubuntu:
  cmd.script:
    - creates: /srv/debrepos/ubuntu/conf/local-packages
    - source: salt://scripts/create-local-packages-list.sh
    - cwd: /srv/debrepos/ubuntu
    - require:
      - cmd: local-packages
      - file: /srv/debrepos/ubuntu/conf
      - file: /srv/debrepos/ubuntu/conf/updates
      - file: /srv/debrepos/ubuntu/conf/distributions
      - file: /srv/debrepos/ubuntu/conf/live-packages

ubuntu-repos-ready:
  cmd.run:
    - name: echo "ubuntu repos ready"
    - user: {{ user }}
    - group: {{ group }}
    - requires:
      - cmd: local-packages-ubuntu

update-ubuntu-repos:
  cmd.run:
    - name: reprepro -VV --noskipold update
    - unless: test -d /srv/debrepos/ubuntu/db
    - user: {{ user }}
    - group: {{ group }}
    - cwd: /srv/debrepos/ubuntu
    - requires:
      - cmd: ubuntu-repos-ready





