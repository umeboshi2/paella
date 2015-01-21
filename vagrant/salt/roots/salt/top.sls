# -*- mode: yaml -*-
{% set pget = salt['pillar.get'] %}
{% set mswin = pget('paella:install_mswindows_machines', False) %}
base:
  'paella':
    - apt-cacher.ng.server
    - apt
    - default
    {% if mswin %}
    - filesystem-mounts
    - samba.config
    {% endif %}
    - binddns
    - apache
    - virtualenv
    - postgresql
    - webdev
    - debrepos
    - paella-client
    {% if mswin %}
    - wimlib
    - winpe
    {% endif %}
    
    #- winbuilder


