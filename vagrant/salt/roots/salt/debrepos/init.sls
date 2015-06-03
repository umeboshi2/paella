# -*- mode: yaml -*-
{% set pget = salt['pillar.get'] %}
{% set user = pget('paella:paella_user', 'vagrant') %}
{% set group = pget('paella:paella_group', 'vagrant') %}
{% macro pkgname(pkg, version, deb) -%}
{{ pkg }}_{{ version }}-paella1_all.{{ deb }}
{%- endmacro %}

{% set oscodename = salt['grains.get']('oscodename') %}
{% if oscodename == 'wheezy': %}
{% set apache_confdir = '/etc/apache2/conf.d' %}
{% else %}
{% set apache_confdir = '/etc/apache2/conf-available' %}
{% endif %}

include:
  - apache
  - debrepos.base
  - debrepos.keys
  - debrepos.saltrepos
  - debrepos.paellarepos
  {%- if pget('paella:make_local_partial_mirror', False) %}
  - debrepos.mainrepos
  - debrepos.secrepos
  - debrepos.ubunturepos
  {% endif %}

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
      - sls: debrepos.saltrepos
      - sls: debrepos.paellarepos
      {%- if pget('paella:make_local_partial_mirror', False) %}
      - sls: debrepos.mainrepos
      - sls: debrepos.secrepos
      - sls: debrepos.ubunturepos
      {% endif %}

# setup apache config
debrepos-apache-config:
  file.managed:
    - name: {{ apache_confdir }}/debrepos
    - source: salt://debrepos/apache.conf
    - template: jinja
    - watch_in:
      - service: apache
        


{%- if pget('paella:make_local_partial_mirror', False) %}
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
{% endif %}

