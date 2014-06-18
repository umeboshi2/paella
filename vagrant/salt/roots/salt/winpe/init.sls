# -*- mode: yaml -*-

#####################################

# winpe
# 
# the local debian repository must be ready


include:
  - samba
  - paella-client
  - wimlib


local_paella_repos_sources_list:
  file.managed:
    - name: /etc/apt/sources.list.d/paella.list
    - contents: deb http://localhost/debrepos/paella wheezy main
    - require:
      - sls: samba
      - sls: paella-client
      - sls: wimlib


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
    - require:
      - cmd: update-apt-after-adding-local-paella-repos


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
    - source: salt://winpe/peauto.bat

example-peauto64.bat:
  file.managed:
    - name: /home/vagrant/workspace/peauto64.bat
    - source: salt://winpe/peauto64.bat

example-bcdauto.bat:
  file.managed:
    - name: /home/vagrant/workspace/bcdauto.bat
    - source: salt://winpe/bcdauto.bat

example-overlay-directory:
  file.directory:
    - name: /var/cache/netboot/winpe
    - makedirs: True

example-autounattend-xml:
  file.managed:
    - name: /var/cache/netboot/winpe/Autounattend.xml
    - source: salt://winpe/Autounattend.xml

example-winpe-files:
  cmd.wait:
    - name: echo "example-winpe-files ready"
    - require:
      - file: example-autounattend-xml
      - file: example-peauto.bat
      - file: example-peauto64.bat
      - file: example-bcdauto.bat



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
    - name: mkwinpeimg -A /srv/shares/aik --iso -s /home/vagrant/workspace/peauto.bat -O /var/cache/netboot/winpe /srv/debrepos/winpe.iso

make-another-test-winpe-iso-amd64:
  cmd.run:
    - user: ${pillar['paella_user']}
    - cwd: /vagrant
    - unless: test -r /srv/debrepos/winpe64.iso
    - require:
      - cmd: example-winpe-files
    - name: mkwinpeimg --arch=amd64 -A /srv/shares/aik --iso -s /home/vagrant/workspace/peauto64.bat -O /var/cache/netboot/winpe /srv/debrepos/winpe64.iso

make-test-winpe-shell-iso:
  cmd.run:
    - user: ${pillar['paella_user']}
    - cwd: /vagrant
    - unless: test -r /srv/debrepos/winpe-shell.iso
    - require:
      - cmd: example-winpe-files
    - name: mkwinpeimg -A /srv/shares/aik --iso /srv/debrepos/winpe-shell.iso

<% bcdauto = '/srv/shares/incoming/bcdauto.iso' %>
make-test-bcdauto-winpe-iso:
  cmd.run:
    - user: ${pillar['paella_user']}
    - cwd: /vagrant
    - unless: test -r ${bcdauto}
    - require:
      - cmd: example-winpe-files
    - name: mkwinpeimg -A /srv/shares/aik --iso -s /home/vagrant/workspace/bcdauto.bat ${bcdauto}

