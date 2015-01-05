# -*- mode: yaml -*-

# This sls is responsible for installing many of  the packages on the
# vagrant machine that will be required in the local debian repository.
{% set pget = salt['pillar.get'] %}
{% set user = pget('paella:paella_user') %}
{% set group = pget('paella:paella_group') %}

include:
  - default
  - saltmaster.base

{#  
# FIXME - get pkgset id's
local-packages-installed:
  cmd.run:
    - name: echo "local-packages-installed"
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
        
#)

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
    - user: {{ user }}
    - group: {{ group }}
    - cwd: /srv/debrepos/debian
    - requires:
      - cmd: apache-ready




