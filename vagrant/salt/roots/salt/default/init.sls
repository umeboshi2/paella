# -*- mode: yaml -*-

include:
  - files

pager:
  pkg.installed:
    - name: most
  alternatives.set:
    - name: pager
    - path: /usr/bin/most

emacs:
  pkg.installed:
    - name: emacs23
  alternatives.set:
    - name: editor
    - path: /usr/bin/emacs23

screen:
  pkg:
    - installed

basic-tools:
  pkg.installed:
    - pkgs:
      - iotop
      - htop
      - rsync


devpackages:
  pkg.installed:
    - pkgs:
      - git-core
      - devscripts
      - cdbs
      - pkg-config
      - rubygems

python-libdev:
  pkg.installed:
    - pkgs:
      - libpq-dev 
      - libjpeg62-dev 
      - libpng12-dev 
      - libfreetype6-dev 
      - liblcms1-dev 
      - libxml2-dev 
      - libxslt1-dev 

python-dev:
  pkg.installed:
    - pkgs:
      - python-dev
      - python-requests
      - virtualenvwrapper
      - python-stdeb

misc-packages:
  pkg.installed:
    - pkgs:
      - bible-kjv
      - ascii
      - fortune-mod
      - cowsay

debian-archive-keyring-build-depends:
  pkg.installed:
    - pkgs:
      - jetring

wimlib-build-depends:
  pkg.installed:
    - pkgs:
      - autoconf
      - automake
      - libtool
      - debhelper
      - autotools-dev
      - pkg-config
      - libfuse-dev
      - libxml2-dev
      - libssl-dev
      - ntfs-3g-dev
      - libattr1-dev
      - attr

wimlib-runtime-depends:
  pkg.installed:
    - pkgs:
      - genisoimage
      - cabextract


bootloader-packages:
  pkg.installed:
    - pkgs:
      - syslinux
      - ipxe
      
disk-tools:
  pkg.installed:
    - pkgs:
      - parted
      - xfsprogs
      - reiserfsprogs
      - btrfs-tools
      - e2fsprogs
      - mdadm
      

# the virtualbox packages will be 
# needed for the live installer
virtualbox-packages:
  pkg.installed:
    - pkgs:
      - virtualbox

# I need this to test virtualbox
test-virtualbox-packages:
  pkg.installed:
    - pkgs:
      - xfce4
      - lightdm

disable-lightdm-service:
  service.disabled:
    - name: lightdm
    - require:
      - pkg: test-virtualbox-packages

kill-lightdm-service:
  service.dead:
    - name: lightdm
    - sig: /usr/sbin/lightdm
    - require:
      - service: disable-lightdm-service

  
python-debrepos-support-packages:
  pkg.installed:
    - pkgs:
      - python-libtorrent
      - python-feedparser


mingw-packages:
  pkg.installed:
    - pkgs:
      - mingw-w64
      - mingw-w64-tools
