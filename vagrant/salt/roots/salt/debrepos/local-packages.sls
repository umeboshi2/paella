# -*- mode: yaml -*-

<% user = pillar['paella_user'] %>
<% group = pillar['paella_group'] %>

include:
  - apache
  - postgresql.base
  - bind
  - dhcpd.base
  - shorewall.base
  - debianlive
  - netboot.base
  - saltmaster.base
  - samba.base
  - pbuilder
  - schroot.base


local-packages-installed:
  cmd.run:
    - name: echo "local-packages-installed"
    - require:
      - sls: apache
      - sls: postgresql.base
      - sls: bind
      - sls: dhcpd.base
      - sls: shorewall.base
      - sls: debianlive
      - sls: netboot.base
      - sls: saltmaster.base
      - sls: samba.base

local-packages:
  cmd.script:
    - creates: /srv/debrepos/debian/conf/local-packages
    - source: salt://scripts/create-local-packages-list.sh
    - cwd: /srv/debrepos/debian
    - require:
      - cmd: repos-ready
      - cmd: local-packages-installed

    

/usr/local/bin/make-master-pkglist:
  file.managed:
    - source: salt://scripts/make-master-pkglist.py
    - mode: 755
    - requires: local-packages

apache-ready:
  cmd.run:
    - name: /etc/init.d/apache2 restart
    - unless: wget -O /dev/null http://localhost/debrepos/
    - requires:
      - cmd: local-packages


update-debrepos:
  cmd.run:
    - name: reprepro -VV --noskipold update
    - unless: test -d /srv/debrepos/debian/db
    - user: ${user}
    - group: ${group}
    - cwd: /srv/debrepos/debian
    - requires:
      - cmd: apache-ready




