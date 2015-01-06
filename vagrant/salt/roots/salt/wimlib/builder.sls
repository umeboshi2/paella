# -*- mode: yaml -*-
{% set pget = salt['pillar.get'] %}
{% set user = pget('paella:paella_user', 'vagrant') %}
{% set group = pget('paella:paella_group', 'vagrant') %}

#####################################

include:
  - wimlib.resources
  # FIXME do I really need to depend on paella-client?
  - paella-client
  
# FIXME - make this work in schroot only and all
# dist arch combos


{% set localrepo = '/vagrant/repos/wimlib-code' %}
{% set workspace = '/home/vagrant/workspace' %}
{% set buildscript = '/home/vagrant/bin/build-wimlib-package' %}
{% set nmap = dict(amd64='', i386='32') %}

{% for dist in ['wheezy',] %}
{% for arch in ['i386', 'amd64']: %}

# FIXME this is stupid
{% set archspace = '%s/%s/%s' % (workspace, dist, arch) %}

wimlib-workspace-dir-{{ dist }}-{{ arch }}:
  file.directory:
    - name: {{ archspace }}
    - makedirs: True
    - user: {{ user }}


wimlib-git-repos-{{ dist }}-{{ arch }}:
  git.latest:
    - name: {{ localrepo }}
    - target: {{ archspace }}/wimlib-code
    - user: {{ user }}
    - rev: 8682c564e55aae964457f183a9b860de3631d4d1
    - require:
      - file: wimlib-workspace-dir-{{ dist }}-{{ arch }}

{% set builddir = '%s/wimlib-code' % archspace %}

build-wimlib-package-{{ dist }}-{{ arch }}:
  cmd.run:
    - require:
      # FIXME is it necessary to require this?
      - cmd: upload-paella-client-package
      - file: build-wimlib-package-script
    - unless: test -r {{ archspace }}/wimlib_1.6.2-1_{{ arch }}.changes
    - name: schroot -c {{ dist }}{{ nmap[arch] }} {{ buildscript }}
    - cwd: {{ builddir }}
    - user: {{ user }}


upload-wimlib-package-{{ dist }}-{{ arch }}:
  cmd.run:
    - require:
      - cmd: build-wimlib-package-{{ dist }}-{{ arch }}
    - unless: test -n "`reprepro -b /srv/debrepos/paella list {{ dist }} wimtools | grep {{ arch }}`"
    - cwd: {{ archspace }}
    - name: reprepro -b /srv/debrepos/paella --ignore=wrongdistribution include {{ dist }} wimlib_1.6.2-1_{{ arch }}.changes
    - user: {{ user }}
{% endfor %}
{% endfor %}

