# -*- mode: yaml -*-
{% set pget = salt['pillar.get'] %}
{% set user = pget('paella_user') %}
{% set group = pget('paella_group') %}

#####################################

include:
  - default
  - debrepos
  - default
  - schroot


{% set cachedir = '/vagrant/vagrant/cache' %}
{% set reposdir = '%s/repos' % cachedir %}

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


#salt-windows-installer-files:
#  git.latest:
#    - name: {{ reposdir }}/salt-windows-install
#    - target: /srv/shares/incoming/salt-windows-install
#    - user: {{ user }}


{% set localrepo = '%s/wimlib-code' % reposdir %}

{% set workspace = '/home/vagrant/workspace' %}

{% set buildscript = '/home/vagrant/bin/build-wimlib-package' %}
build-wimlib-package-script:
  file.managed:
    - name: {{ buildscript }}
    - source: salt://scripts/build-wimlib-package.sh
    - mode: 755
    - user: {{ user }}
    - makedirs: True


{% for arch in ['i386', 'amd64']: %}

# FIXME this is stupid
{% set archspace = '%s/%s' % (workspace, arch) %}

wimlib-workspace-dir-{{ arch }}:
  file.directory:
    - name: {{ archspace }}
    - makedirs: True
    - user: {{ user }}


wimlib-git-repos-{{ arch }}:
  git.latest:
    - name: {{ localrepo }}
    - target: {{ archspace }}/wimlib-code
    - user: {{ user }}
    - rev: 8682c564e55aae964457f183a9b860de3631d4d1
    - require:
      - file: wimlib-workspace-dir-{{ arch }}

{% set builddir = '%s/wimlib-code' % archspace %}

build-wimlib-package-{{ arch }}:
  cmd.run:
    - require:
      - cmd: upload-paella-client-package
      - file: build-wimlib-package-script
    - unless: test -r {{ archspace }}/wimlib_1.6.2-1_{{ arch }}.changes
    {% if arch == 'amd64': %}
    - name: {{ buildscript }}
    {% elif arch == 'i386': %}
    - name: schroot -c wheezy32 {{ buildscript }}
    {% else: %}
    - name: /bin/false
    {% endif %}
    - cwd: {{ builddir }}
    - user: {{ user }}


upload-wimlib-package-{{ arch }}:
  cmd.run:
    - require:
      - cmd: build-wimlib-package-{{ arch }}
    - unless: test -n "`reprepro -b /srv/debrepos/paella list wheezy wimtools | grep {{ arch }}`"
    - cwd: {{ archspace }}
    - name: reprepro -b /srv/debrepos/paella --ignore=wrongdistribution include wheezy wimlib_1.6.2-1_{{ arch }}.changes
    - user: {{ user }}
{% endfor %}

