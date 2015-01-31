# -*- mode: yaml -*-
{% from 'config.jinja' import paella %}
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
  install_mswindows_machines: {{ paella.install_mswindows_machines }}
  make_local_partial_mirror: {{ paella.make_local_partial_mirror }}
  get_upstream_ipxe: {{ paella.get_upstream_ipxe }}
  get_extra_iso_files: {{ paella.get_extra_iso_files }}
  build_nodejs_deb: {{ paella.build_nodejs_deb }}
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
  
{% set apt_http_proxy = "http://127.0.0.1:8000/" %}
{% if paella.use_local_apt_cache_proxy %}
{% set apt_http_proxy = paella.local_apt_cache_proxy %}
{% endif %}

apt:
  configs:
    02proxy:
      content: |
        Acquire::http { Proxy "{{ apt_http_proxy }}"; };
        
  lookup:
    remove_popularitycontest: true
  repos:
    {% for debtype in ['deb', 'deb-src'] %}
    {% for dist in ['wheezy', 'wheezy-updates'] %}
    vagrant-{{ dist }}-{{ debtype }}-pkgrepo:
      ensure: absent
      debtype: {{ debtype }}
      url: http://mirrors.kernel.org/debian
      dist: {{ dist }}
      comps:
        - main
    paella-{{ dist }}-{{ debtype }}-pkgrepo:
      ensure: managed
      debtype: {{ debtype }}
      url: {{ paella.debian_mirror }}
      dist: {{ dist }}
      globalfile: true
      comps:
        - main
    {% endfor %}
    {% endfor %}
    backports-pkgrepo:
      url: {{ paella.debian_mirror }}
      globalfile: true
      dist: wheezy-backports
        

# FIXME make a password for dbadmin and get rid of
# trust in acls
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
      - .saltstack.com
      - localhost
      - .gatech.edu
