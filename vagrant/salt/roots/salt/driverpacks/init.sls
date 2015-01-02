# -*- mode: yaml -*-
{% set pget = salt['pillar.get'] %}
{% set user = pget('paella_user') %}
{% set group = pget('paella_group') %}



include:
  - driverpacks.base
  - virtualenv

# I haven't decided entirely how to use this yet.
# There is already a debrepos dependency in the
# paella setup.py that links to the github repo.
debrepos-github:
  git.latest:
    - name: https://github.com/umeboshi2/debrepos.git
    - target: /home/vagrant/workspace/debrepos
    - user: {{ user }}
    - rev: af38fcc8928bb542924702da89fdc1a43104b22a

get-driverpacks-script:
  file.managed:
    - name: /usr/local/bin/get-driverpacks
    - source: salt://scripts/get-driverpacks.py
    - mode: 755
    - require:
      - git: debrepos-github


