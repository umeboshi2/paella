# -*- mode: yaml -*-
{% from 'bvars.jinja' import paella %}

paella:  
  # The default is to operate in a vagrant virtual machine.
  # In order for some ofthe states to work, the paella_user 
  # must be able to use sudo without a password.
  paella_user: {{ paella.paella_user }}
  paella_group: {{ paella.paella_group }}

  # If you already have a local mirror, set this to True
  use_local_mirror_for_vagrant: False

  debian_archive_keyring_versions:
    wheezy: 2014.1~deb7u1
    jessie: 2014.3
  virtualenv_basedir: /var/lib/paella
  node_version: 0.10.25
  install_mswindows_machines: False
  make_local_partial_mirror: False



#paella_virtualenv_basedir: /var/lib/paella

#node_version: 0.10.25

apt_cacher_ng:
  #server_cache_dir: /vagrant/cache/apt-cacher-ng
  server_cache_dir_mode: '0755'
  admin_account: vagrant
  admin_passwd: vagrant
  user: vagrant
  group: vagrant
  #no_cache_requested: 10.0.2.1
  
    
rsyslog:
  listentcp: true
  listenudp: true
  logbasepath: /var/log/minions
  

apt:
  configs:
    02proxy:
      content: |
        Acquire::http { Proxy "http://127.0.0.1:3142"; };
        
  lookup:
    remove_popularitycontest: true
  repos:
    littledebian-paella-pkgrepo:
      url: http://debrepos.littledebian.org/paella
      keyuri: http://debrepos.littledebian.org/littledebian.key
      globalfile: true
      dist: wheezy
