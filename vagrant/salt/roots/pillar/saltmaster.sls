# -*- mode: yaml -*-

saltmaster:
  open_mode: True
  auto_accept: True
  renderer: yaml_mako
  hash_type: sha256
  top_gitfs_remote: https://github.com/umeboshi2/paella-states.git
  top_ext_git_pillar: master https://github.com/umeboshi2/paella-pillar.git

