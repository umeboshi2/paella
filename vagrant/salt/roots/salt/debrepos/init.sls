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
      
      
keyring-package-build-dependencies:
  pkg.installed:
    - pkgs:
      - jetring


build-keyring-package:
  cmd.script:
    - source: salt://scripts/build-keyring-package.sh
    - unless: test -d /home/vagrant/workspace
    - user: ${user}
    - group: ${group}
    - requires:
      - cmd: update-debrepos


