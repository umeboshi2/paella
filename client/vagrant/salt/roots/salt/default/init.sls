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
    - name: emacs24
  alternatives.set:
    - name: editor
    - path: /usr/bin/emacs24

screen:
  pkg:
    - installed

basic-tools:
  pkg.installed:
    - pkgs:
      - iotop
      - htop

# some of this is needed for
# building the nodejs package
devpackages:
  pkg.installed:
    - pkgs:
      - git-core
      - devscripts
      - cdbs
      - pkg-config
      - curl
      - zlib1g-dev
      - rubygems
      - ruby-dev
      
