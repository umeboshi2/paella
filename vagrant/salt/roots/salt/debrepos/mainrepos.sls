# -*- mode: yaml -*-
{% set pget = salt['pillar.get'] %}
{% set user = pget('paella:paella_user') %}
{% set group = pget('paella:paella_group') %}

include:
  - default
  - services.apache
  #- postgresql.base
  #- bind
  #- dhcpd.base
  #- shorewall.base
  #- debianlive
  #- netboot.base
  #- saltmaster.base
  #- samba.base
  #- pbuilder
  #- schroot.base


/srv/debrepos/debian/conf:
  file.directory:
    - makedirs: True

{% for dist in ['wheezy', 'jessie']: %}
{% for arch in ['i386', 'amd64']: %}
{% set upstream_filename = '/srv/debrepos/debian/conf/udebs-%s-%s-upstream' % (dist, arch) %}
{% set list_filename = '/srv/debrepos/debian/conf/%s-%s-udeb.list' % (dist, arch) %}
create-udeb-list-{{ dist }}-{{ arch }}:
  cmd.run:
    - unless: test -r {{ list_filename }}
    - name: awk '{print $1 "\tinstall"}' < {{ upstream_filename }} > {{ list_filename }}
    - requires:
        - file: udeb-list-upstream-{{ dist }}-{{ arch }}
    - creates: {{ list_filename }}
{% endfor %}
{% endfor %}


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
    - user: {{ user }}
    - group: {{ group }}
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
      - pkg: basic-tools
      - pkg: devpackages
      - pkg: python-dev
      - pkg: python-libdev
      - pkg: misc-packages
      - pkg: debian-archive-keyring-build-depends
      - pkg: wimlib-build-depends
      - pkg: wimlib-build-depends-extra
      - pkg: wimlib-runtime-depends
      - pkg: bootloader-packages
      - pkg: installer-disktools
      - pkg: mingw-packages
      - pkg: live-system-dekstop-packages
      - pkg: live-image-packages
      - pkg: virtualbox-packages
      - pkg: apache-support-packages
      - pkg: apache-package
      - pkg: bind9
      - pkg: live-build
      - pkg: reprepro
      - pkg: germinate
      - pkg: python-debrepos-support-packages
      - pkg: postgresql-support-packages
      - pkg: postgresql-package
      - pkg: isc-dhcp-server-package
      - pkg: shorewall-package
      - pkg: nfs-kernel-server-package
      - pkg: tftpd-package
      - pkg: samba-support-packages
      - pkg: samba-server-package
      - pkg: schroot-packages

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
    - user: {{ user }}
    - group: {{ group }}
    - cwd: /srv/debrepos/debian
    - requires:
      - cmd: apache-ready




