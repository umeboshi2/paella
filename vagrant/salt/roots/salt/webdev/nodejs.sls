# -*- mode: yaml -*-
{% set pget = salt['pillar.get'] %}

include:
  - default.pkgsets
  
{% set repodir = '/vagrant/repos' %}
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
    - unless: test -x /usr/bin/npm
    - source: salt://webdev/files/build-nodejs.sh
    - env:
      - NODE_VERSION: {{ pget('node_version') }}
      # YAML inconsistency.  Should these be recast to strings in salt?
      - DEBIAN_CONCURRENCY: "3"

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
