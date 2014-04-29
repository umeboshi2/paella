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
    - rev: f303b46312f8d8be4210fba66082d5a7572dbd70

# This darned command should almost be a script.
# In order to keep the development base and partial
# debian repository reasonably small, the building 
# of the doc package is bypassed.  The tests are 
# also bypassed as they require extra build depends,
# as well as being root, instead of fakeroot.  The
# tests for this build passed when the package was 
# built manually.
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

# the mkwinpeimage command depends on the mkisofs 
# command being in the PATH.
# FIXME
# make the symlink somewhere else and append that 
# to PATH in the evironment where mkwinpeimage will
# be used.  This will help find other tools that
# depend on the mkisofs command. 
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

example-overlay-directory:
  file.directory:
    - name: /var/cache/netboot/winpe
    - makedirs: True

example-autounattend-xml:
  file.managed:
    - name: /var/cache/netboot/winpe/Autounattend.xml
    - source: salt://files/Autounattend.xml

example-winpe-files:
  cmd.wait:
    - name: echo "example-winpe-files ready"
    - require:
      - file: example-autounattend-xml
      - file: example-peauto.bat


# This command demonstrates the reason for the 
# all the trouble required to get the AIK and 
# wimlib setup properly.  This state will 
# disappear eventually when I make a more generic
# image and/or other special images.
make-test-winpe-iso:
  cmd.run:
    - user: ${pillar['paella_user']}
    - cwd: /vagrant
    - unless: test -r /vagrant/testme-peauto.iso
    - require:
      - cmd: example-winpe-files
    - name: mkwinpeimg -A /srv/shares/aik --iso -s /home/vagrant/workspace/peauto.bat /vagrant/testme-peauto.iso

make-another-test-winpe-iso:
  cmd.run:
    - user: ${pillar['paella_user']}
    - cwd: /vagrant
    - unless: test -r /srv/debrepos/winpe.iso
    - require:
      - cmd: example-winpe-files
    # this is a simple image
    #- name: mkwinpeimg -A /srv/shares/aik --iso /srv/debrepos/winpe.iso
    - name: mkwinpeimg -A /srv/shares/aik --iso -s /home/vagrant/workspace/peauto.bat -O /var/cache/netboot/winpe /srv/debrepos/winpe.iso

