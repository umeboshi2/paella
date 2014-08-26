# -*- mode: yaml -*-

/var/cache/vagrant:
  file.directory:
    - user: vagrant
    - group: vagrant
    - dir_mode: 755
    - file_mode: 644
    - makedirs: True
    - recurse:
        - user
        - group
        - mode

