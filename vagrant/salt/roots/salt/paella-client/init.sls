# -*- mode: yaml -*-

#####################################

# paella-client
# 
# the local debian repository must be ready

include:
  - debrepos

build-paella-client-package:
  cmd.run:
    - require:
      - sls: debrepos
    - unless: test -r /srv/src/paella-client_0.1dev-1_i386.changes
    - name: debuild --no-lintian --no-tgz-check -us -uc
    - cwd: /srv/src/paella-client
    - user: vagrant

upload-paella-client-package:
  cmd.run:
    - require:
      - cmd: build-paella-client-package
    - unless: test -n "`reprepro -b /srv/debrepos/paella list wheezy python-paella-client`"
    - cwd: /srv/src
    - name: reprepro -b /srv/debrepos/paella --ignore=wrongdistribution include wheezy paella-client_0.1dev-1_i386.changes
    - user: vagrant

