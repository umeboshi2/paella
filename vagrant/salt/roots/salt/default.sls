# -*- mode: yaml -*-

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
      - attr-dev
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
