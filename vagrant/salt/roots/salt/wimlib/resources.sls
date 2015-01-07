# -*- mode: yaml -*-
{% set pget = salt['pillar.get'] %}
{% set user = pget('paella:paella_user', 'vagrant') %}
{% set group = pget('paella:paella_group', 'vagrant') %}

#####################################

include:
  - default.pkgsets
  - debrepos
  - schroot


{% set reposdir = '/vagrant/repos' %}

cache-wimlib-git-repos:
  git.latest:
    - name: git://git.code.sf.net/p/wimlib/code
    - target: {{ reposdir }}/wimlib-code
    - user: {{ user }}
    - rev: 8682c564e55aae964457f183a9b860de3631d4d1

# FIXME: find a better place for this state
salt-windows-installer-files-git-repos-cache:
  git.latest:
    - name: https://github.com/saltstack/salt-windows-install.git
    - target: {{ reposdir }}/salt-windows-install
    - user: {{ user }}
    - rev: 36a7b90f8a7b90aad25c5190fa032ab6eaf6a405


salt-windows-installer-files:
  git.latest:
    - name: {{ reposdir }}/salt-windows-install
    - target: /srv/shares/incoming/salt-windows-install
    #- user: {{ user }}


{% set localrepo = '%s/wimlib-code' % reposdir %}

{% set workspace = '/home/vagrant/workspace' %}

{% set buildscript = '/home/vagrant/bin/build-wimlib-package' %}
build-wimlib-package-script:
  file.managed:
    - name: {{ buildscript }}
    - source: salt://wimlib/files/build-wimlib-package.sh
    - mode: 755
    - user: {{ user }}
    - makedirs: True


