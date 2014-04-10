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

screen:
  pkg:
    - installed

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
