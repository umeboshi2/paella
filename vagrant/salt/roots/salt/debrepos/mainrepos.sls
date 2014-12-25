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


/srv/debrepos/debian/conf:
  file.directory:
    - makedirs: True

<% checksums = pillar['debian_installer_i386_checksums'] %>
<% DI = pillar['debian_pxe_installer'] %>
%for dist in DI:
%for arch in DI[dist]:
<% upstream_filename = '/srv/debrepos/debian/conf/udebs-%s-%s-upstream' % (dist, arch) %>
<% list_filename = '/srv/debrepos/debian/conf/%s-%s-udeb.list' % (dist, arch) %>
udeb-list-upstream-${dist}-${arch}:
  file.managed:
    - name: ${upstream_filename}
    - source: ${DI[dist][arch]['udeb_list']['source']}
    - source_hash: ${DI[dist][arch]['udeb_list']['source_hash']}
    - requires:
      - file: /srv/debrepos/debian/conf

create-udeb-list-${dist}-${arch}:
  cmd.run:
    - unless: test -r ${list_filename}
    - name: awk '{print $1 "\tinstall"}' < ${upstream_filename} > ${list_filename}
    - requires:
        - file: udeb-list-upstream-${dist}-${arch}
    - creates: ${list_filename}
%endfor      
%endfor      


/srv/debrepos/debian/conf/live-packages:
  file.managed:
    - source: salt://debrepos/live-packages

/srv/debrepos/debian/conf/jessie-pkgs:
  file.managed:
    - source: salt://debrepos/jessie-pkgs

/srv/debrepos/debian/conf/updates:
  file.managed:
    - source: salt://debrepos/repos/debian/updates
    - template: mako

/srv/debrepos/debian/conf/distributions:
  file.managed:
    - source: salt://debrepos/repos/debian/distributions
    - template: mako

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


local-packages:
  cmd.script:
    - creates: /srv/debrepos/debian/conf/local-packages
    - source: salt://scripts/create-local-packages-list.sh
    - cwd: /srv/debrepos/debian
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




