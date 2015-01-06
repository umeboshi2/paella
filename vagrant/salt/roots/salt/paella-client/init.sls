# -*- mode: yaml -*-
{% set pget = salt['pillar.get'] %}
{% set user = pget('paella:paella_user', 'vagrant') %}
{% set group = pget('paella:paella_group', 'vagrant') %}

#####################################

# paella-client
# 
# the local debian repository must be ready

include:
  - default.pkgsets
  - debrepos


build-paella-client-package:
  cmd.run:
    - require:
      - sls: debrepos
    - unless: test -r /srv/src/paella-client_0.1dev-1_amd64.changes
    - name: debuild --no-lintian --no-tgz-check -us -uc
    - cwd: /srv/src/paella-client
    - user: {{ user }}

upload-paella-client-package:
  cmd.run:
    - require:
      - cmd: build-paella-client-package
    - unless: test -n "`reprepro -b /srv/debrepos/paella list wheezy python-paella-client`"
    - cwd: /srv/src
    - name: reprepro -b /srv/debrepos/paella --ignore=wrongdistribution include wheezy paella-client_0.1dev-1_amd64.changes
    - user: {{ user }} 
