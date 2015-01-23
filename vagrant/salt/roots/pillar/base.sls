# -*- mode: yaml -*-
{% from 'bvars.jinja' import paella %}
{% set mswin = paella.install_mswindows_machines %}

paella:  
  # The default is to operate in a vagrant virtual machine.
  # In order for some ofthe states to work, the paella_user 
  # must be able to use sudo without a password.
  paella_user: {{ paella.paella_user }}
  paella_group: {{ paella.paella_group }}

  # If you already have a local mirror, set this to True
  use_local_mirror_for_vagrant: False

  virtualenv_basedir: /var/lib/paella
  node_version: 0.10.29
  install_mswindows_machines: False
  make_local_partial_mirror: False
  top_states:
    #- apt-cacher.ng.server
    - apt.repos
    - squid
    - squid.debproxy
    - apt.config
    - apt
    - default
    {% if mswin %}
    - filesystem-mounts
    - samba.config
    {% endif %}
    - binddns
    - virtualenv
    - apache
    - apache.mod_wsgi
    - postgres
    - debrepos
    - webdev
    - paella-client
    - mainserver
    {% if mswin %}
    - driverpacks
    - wimlib
    - winpe
    {% endif %}
    - paella-netboot

  # these are only needed if building a local
  # partial mirror
  debian_archive_keyring_versions:
    wheezy: 2014.1~deb7u1
    jessie: 2014.3

rsyslog:
  listentcp: true
  listenudp: true
  logbasepath: /var/log/minions
  

apt:
  configs:
    02proxy:
      content: |
        Acquire::http { Proxy "http://127.0.0.1:8000"; };
        
  lookup:
    remove_popularitycontest: true
  repos:
    backports-pkgrepo:
      url: http://http.debian.net/debian
      globalfile: true
      dist: wheezy-backports
    littledebian-paella-pkgrepo:
      url: http://debrepos.littledebian.org/paella
      keyuri: http://debrepos.littledebian.org/littledebian.key
      globalfile: true
      dist: wheezy


postgres:
  lookup:
    pkg_dev: False
  users:
    dbadmin:
      createdb: true
  acls:
    - ['local', 'paella', 'dbadmin', 'trust']
    - ['host', 'paella', 'dbadmin', '127.0.0.0/12', 'trust']

  databases:
    paella:
      owner: 'dbadmin'
      # FIXME, I would rather get the formulas working
      # appropriately
      # https://github.com/saltstack/salt/issues/19924
      template: 'template0'
  #postgresconf: |
  #  listen_addresses = 'localhost,*'
  pg_hba.conf: salt://postgres/pg_hba.conf


squid:
  debproxy:
    dstdomains:
      - .kernel.org
      - .debian.net
      - .littledebian.org
      - .saltstack.com
      - localhost