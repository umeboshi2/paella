# -*- mode: yaml -*-

<% user = pillar['paella_user'] %>
<% group = pillar['paella_group'] %>


/srv/debrepos/debian/conf:
  file.directory:
    - makedirs: True


i386-udeb-list-upstream:
  file.managed:
    - name: /srv/debrepos/debian/conf/i386-udeb-list-upstream
    - source: http://ftp.us.debian.org/debian/dists/wheezy/main/installer-i386/current/images/udeb.list
    - source_hash: sha256=15ce82c5c843a4d752932e05596a3ae22d7575e4b713a27a4367a7d2697a5777
    - requires:
      - file: /srv/debrepos/debian/conf

create-udeb-list:
  cmd.run:
    - unless: test -r /srv/debrepos/debian/conf/i386-udeb-list
    - name: cat /srv/debrepos/debian/conf/i386-udeb-list-upstream | awk '{print $1 "\tinstall"}' > /srv/debrepos/debian/conf/i386-udeb-list
    - requires:
      - file: i386-udeb-list-upstream
    - creates: 


/srv/debrepos/debian/conf/live-packages:
  file.managed:
    - source: salt://debrepos/live-packages

/srv/debrepos/debian/conf/updates:
  file.managed:
    - source: salt://debrepos/repos/debian/updates

/srv/debrepos/debian/conf/distributions:
  file.managed:
    - source: salt://debrepos/repos/debian/distributions

repos-ready:
  cmd.run:
    - name: echo "repos-ready"
    - user: ${user}
    - group: ${group}
    - cwd: /srv/debrepos/debian
    - requires:
      - cmd: create-udeb-list
      - cmd: keyring-ready
      - file: /srv/debrepos/debian/conf/live-packages
      - file: /srv/debrepos/debian/conf/updates
      - file: /srv/debrepos/debian/conf/distributions

include:
  - apache
  - postgresql
  - tftpd
  - bind
  - dhcpd
  - shorewall
  - squid
  - debianlive
  - netboot-base


local-packages:
  cmd.script:
    - creates: /srv/debrepos/debian/conf/local-packages
    - source: salt://scripts/create-local-packages-list.sh
    - cwd: /srv/debrepos/debian
    - require:
      - sls: apache
      - sls: postgresql
      - sls: tftpd
      - sls: bind
      - sls: dhcpd
      - sls: shorewall
      - sls: debianlive
      - sls: netboot-base
      - pkg: squid
      - cmd: repos-ready

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




