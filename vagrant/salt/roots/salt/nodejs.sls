# -*- mode: yaml -*-

include:
  - default

node-debian-git-repo:
  git.latest:
    - name: https://github.com/mark-webster/node-debian
    - target: /srv/node-debian

node-debian-build-repo:
  git.latest:
    - require:
      - git: node-debian-git-repo
    - name: /srv/node-debian
    - target: /var/tmp/make-nodejs/node-debian




build-nodejs-package:
  cmd.script:
    - require:
      - sls: default
      - git: node-debian-build-repo
    - unless: test -x /usr/bin/npm
    - source: salt://files/build-nodejs.sh
    - env:
      - NODE_VERSION: ${pillar['node_version']}

nodejs:
  pkg.installed:
    - require:
      - cmd: build-nodejs-package


%for pkg in ['coffee-script', 'grunt-cli', 'bower', 'http-server']:

npm-${pkg}:
  npm.installed:
    - require:
      - pkg: nodejs
    - name: ${pkg}
%endfor
