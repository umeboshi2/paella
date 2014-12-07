# -*- mode: yaml -*-

saltmaster:
  daemon_loglevel: debug
  open_mode: False
  auto_accept: False
  renderer: yaml_mako
  hash_type: sha256
  #use_gitfs_remote: True
  use_gitfs_remote: False
  top_gitfs_remote: https://github.com/umeboshi2/paella-states.git
  base_fileserver_root: /vagrant/vagrant/paella/salt

  base_pillar_root: /vagrant/vagrant/paella/pillar
  #use_ext_git_pillar: True
  use_ext_git_pillar: False
  top_ext_git_pillar: master https://github.com/umeboshi2/paella-pillar.git
