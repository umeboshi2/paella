# -*- mode: yaml -*-

saltmaster:
  daemon_loglevel: debug
  open_mode: False
  auto_accept: False
  renderer: yaml_jinja
  hash_type: sha256
  #use_gitfs_remote: True
  use_gitfs_remote: true
  gitfs_remotes:
    - https://github.com/umeboshi2/saltstack-formulae.git
    - https://github.com/umeboshi2/paella-states.git
  base_fileserver_root: /vagrant/paella/salt

  base_pillar_root: /vagrant/paella/pillar
  #use_ext_git_pillar: True
  use_ext_git_pillar: True
  top_ext_git_pillar: master https://github.com/umeboshi2/paella-pillar.git

  file_roots:
    - base:
      - /srv/salt
    
    
    