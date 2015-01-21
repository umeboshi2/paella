# -*- mode: yaml -*-
{% set pget = salt['pillar.get'] %}

include:
  - default.pkgsets
  
{% set repodir = '/vagrant/repos' %}
{% set node_version = pget('paella:node_version', '0.10.26') %}
node-debian-git-repo:
  git.latest:
    # replace with mark-webster upstream if/when pull request accepted
    #- name: https://github.com/mark-webster/node-debian.git
    - name: https://github.com/umeboshi2/node-debian.git
    - target: {{ repodir }}/node-debian

node-debian-build-repo:
  git.latest:
    - require:
      - git: node-debian-git-repo
    - name: {{ repodir }}/node-debian
    - target: /var/tmp/make-nodejs/node-debian




build-nodejs-package:
  cmd.script:
    - require:
      - pkg: devpackages
      - pkg: python-dev
      - pkg: python-libdev
      - pkg: wimlib-build-depends
      - git: node-debian-build-repo
    - unless: test -r /var/tmp/make-nodejs/node-debian/nodejs_{{ node_version }}-1_amd64.deb || test -n "`reprepro -b /srv/debrepos/paella list wheezy nodejs`"
    - source: salt://webdev/files/build-nodejs.sh
    - env:
      - NODE_VERSION: {{ node_version }}
      # YAML inconsistency.  Should these be recast to strings in salt?
      - DEBIAN_CONCURRENCY: "3"

upload-nodejs-package:
  cmd.run:
    - require:
      - cmd: build-nodejs-package
    - unless: test -n "`reprepro -b /srv/debrepos/paella list wheezy nodejs`"
    - cwd: /var/tmp/make-nodejs/node-debian
    - name: reprepro -b /srv/debrepos/paella --ignore=wrongdistribution include wheezy nodejs_{{ node_version }}-1_amd64.changes
    - user: {{ user }} 

nodejs:
  pkg.installed:
    - require:
      - cmd: build-nodejs-package

npm-webdev-packages:
  npm.installed:
    - require:
      - pkg: nodejs
    - pkgs:
      - coffee-script
      - grunt-cli
      - bower
      - http-server
      - js2coffee
      - express
