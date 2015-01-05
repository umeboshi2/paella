# -*- mode: yaml -*-
{% set pget = salt['pillar.get'] %}
{% set user = pget('paella:paella_user') %}
{% set group = pget('paella:paella_group') %}
{% macro pkgname(pkg, version, deb) -%}
{{ pkg }}_{{ version }}-paella1_all.{{ deb }}
{%- endmacro %}

include:
  - services.apache
  - debrepos.base
  - debrepos.keys
  - debrepos.mainrepos
  - debrepos.saltrepos
  - debrepos.secrepos
  - debrepos.paellarepos

#extend:
#  apache-service:
#    - service:
#        - watch:
#            - file: debrepos-apache-config
        
debrepos-ready:
  cmd.run: 
    - name: echo "debrepos-ready"
    - require:
      - sls: debrepos.base
      - sls: debrepos.keys
      - sls: debrepos.mainrepos
      - sls: debrepos.saltrepos
      - sls: debrepos.secrepos
      - sls: debrepos.paellarepos

# setup apache config
debrepos-apache-config:
  file.managed:
    - name: /etc/apache2/conf.d/debrepos
    - source: salt://debrepos/apache.conf
    - template: jinja
    #- require_in:
    #  - service: apache-service
    - watch_in:
      - service: apache-service

# This script will rebuild the debian-archive-keyring
# package with the paella repository key inserted.

{% for dist in pget('paella:debian_archive_keyring_versions'): %}
{% set version = pget('paella:debian_archive_keyring_versions')[dist] %}
{% set changes = '/home/vagrant/workspace/debian-archive-keyring_%s-paella1_amd64.changes' % version %}
build-keyring-package-{{ dist }}:
  cmd.script:
    - source: salt://scripts/build-keyring-package.py
    - unless: test -r {{ changes }}
    - args: "-d {{ dist }} -v {{ version }} -w /home/vagrant/workspace"
    - user: {{ user }}
    - group: {{ group }}
    - requires:
      - cmd: update-debrepos
{% set dirname = '/srv/debrepos/debian/pool/main/d/debian-archive-keyring' %}
{% for deb in ['deb', 'udeb']: %}
{% set pkg = 'debian-archive-keyring' %}
{% if deb == 'udeb' %}
{% set pkg = '%s-udeb' % pkg %}
{% endif %}
{% set basename = pkgname(pkg, version, deb) %}
upload-keyring-package-{{ dist}}-{{ deb }}:
  cmd.run:
    - name: reprepro -b /srv/debrepos/debian --ignore=wrongdistribution include{{ deb }} {{ dist }} {{ basename }}
    - unless: test -r {{ dirname }}/{{ basename }}
    - user: {{ user }}
    - group: {{ group }}
    - cwd: /home/vagrant/workspace
{% endfor %}    
{% endfor %}      

