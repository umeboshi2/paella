# -*- mode: yaml -*-

#####################################

# paella-client
# 
# the local debian repository must be ready

include:
  - debrepos
  - default


build-paella-client-package:
  cmd.run:
    - require:
      - sls: debrepos
    - unless: test -r /srv/src/paella-client_0.1dev-1_i386.changes
    - name: debuild --no-lintian --no-tgz-check -us -uc
    - cwd: /srv/src/paella-client
    - user: ${pillar['paella_user']}

upload-paella-client-package:
  cmd.run:
    - require:
      - cmd: build-paella-client-package
    - unless: test -n "`reprepro -b /srv/debrepos/paella list wheezy python-paella-client`"
    - cwd: /srv/src
    - name: reprepro -b /srv/debrepos/paella --ignore=wrongdistribution include wheezy paella-client_0.1dev-1_i386.changes
    - user: ${pillar['paella_user']}


wimlib-git-repos:
  git.latest:
    - name: git://git.code.sf.net/p/wimlib/code
    - target: /home/vagrant/workspace/wimlib-code
    - user: ${pillar['paella_user']}

build-wimlib-package:
  cmd.run:
    - require:
      - cmd: upload-paella-client-package
    #- unless: test -r /srv/src/paella-client_0.1dev-1_i386.changes
    - unless: /bin/true
    - name: debuild --no-lintian --no-tgz-check -us -uc
    - cwd: /srv/src/paella-client
    - user: ${pillar['paella_user']}
