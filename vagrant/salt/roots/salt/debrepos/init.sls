# -*- mode: yaml -*-

<% user = pillar['paella_user'] %>
<% group = pillar['paella_group'] %>

include:
  - debrepos.base
  - debrepos.keys
  - debrepos.mainrepos
  - debrepos.saltrepos
  - debrepos.secrepos
  - debrepos.paellarepos

debrepos-ready:
  cmd.run: 
    - name: echo "debrepos-ready"
    - require:
      - sls: debrepos.base
      - sls: debrepos.keys
      - sls: debrepos.mainrepos
      - sls: debrepos.saltrepos
      - sls: debrepos.secrepos
      - sls: debrepos.paellarepos
      
# This script will rebuild the debian-archive-keyring
# package with the paella repository key inserted.
# FIXME  This script only works if the package is
# built manually and the appropriate signatures
# placed in the script.
# The fix should be to attempt to build the package
# gather and store the correct signatures, destroy
# the failed build and build again with correct
# signatures.  This script may be need to be
# written in python to more easily achieve this.

build-keyring-package:
  cmd.script:
    - source: salt://scripts/build-keyring-package.sh
    - unless: test -r /home/vagrant/workspace/debian-archive-keyring_2014.1~deb7u1-paella1_amd64.changes
    - user: ${user}
    - group: ${group}
    - requires:
      - cmd: update-debrepos


# FIXME make one script instead of one for each release        
build-keyring-package-jessie:
  cmd.script:
    - source: salt://scripts/build-keyring-package-jessie.sh
    - unless: test -r /home/vagrant/workspace/jessie/debian-archive-keyring_2014.3-paella1_amd64.changes
    - user: ${user}
    - group: ${group}
    - requires:
      - cmd: update-debrepos


