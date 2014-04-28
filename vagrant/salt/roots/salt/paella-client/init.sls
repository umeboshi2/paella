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
    - unless: test -r /home/vagrant/workspace/wimlib_1.6.2-1_i386.changes
    - name: debuild --no-lintian --no-tgz-check -us -uc
    - name: rm -f debian/wimlib-doc.docs debian/wimlib-doc.examples && ./bootstrap && env DEB_BUILD_OPTIONS=nocheck DEBUILD_DPKG_BUILDPACKAGE_OPTS="-B" debuild --preserve-envvar=DEB_BUILD_OPTIONS --preserve-envvar=DEBUILD_DPKG_BUILDPACKAGE_OPTS --no-lintian --no-tgz-check -us -uc -d

    - cwd: /home/vagrant/workspace/wimlib-code
    - user: ${pillar['paella_user']}


upload-wimlib-package:
  cmd.run:
    - require:
      - cmd: build-wimlib-package
    - unless: test -n "`reprepro -b /srv/debrepos/paella list wheezy wimtools`"
    - cwd: /home/vagrant/workspace
    - name: reprepro -b /srv/debrepos/paella --ignore=wrongdistribution include wheezy wimlib_1.6.2-1_i386.changes
    - user: ${pillar['paella_user']}


local_paella_repos_sources_list:
  file.managed:
    - name: /etc/apt/sources.list.d/paella.list
    - contents: deb http://localhost/debrepos/paella wheezy main
    - require:
      - cmd: upload-wimlib-package

update-apt-after-adding-local-paella-repos:
  cmd.wait:
    - name: apt-get -y update
    - require:
      - file: local_paella_repos_sources_list
    - watch:
      - file: local_paella_repos_sources_list

wimlib-packages:
  pkg.installed:
    - pkgs:
      - wimtools

legacy-mkisofs-symlink:
  file.symlink:
    - name: /usr/local/bin/mkisofs
    - target: /usr/bin/genisoimage
    - require:
      - pkg: wimlib-runtime-depends

example-peauto.bat:
  file.managed:
    - name: /home/vagrant/workspace/peauto.bat
    - source: salt://paella-client/peauto.bat

make-test-winpe-iso:
  cmd.run:
    - user: ${pillar['paella_user']}
    - cwd: /vagrant
    - unless: test -r /vagrant/testme-peauto.iso
    - name: mkwinpeimg -A /srv/shares/aik --iso -s /home/vagrant/workspace/peauto.bat /vagrant/testme-peauto.iso
