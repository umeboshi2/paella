# -*- mode: yaml -*-
{% set pget = salt['pillar.get'] %}

include:
  - default
  
{% set repodir = '/vagrant/vagrant/cache/repos' %}
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
      - sls: default
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


{% for pkg in ['coffee-script', 'grunt-cli', 'bower', 'http-server', 'js2coffee']: %}

npm-{{ pkg }}:
  npm.installed:
    - require:
      - pkg: nodejs
    - name: {{ pkg }}
{% endfor %}
