# -*- mode: yaml -*-

/var/lib/paella:
  file.directory:
    - makedirs: True


/var/lib/paella/venv:
  virtualenv.managed:
    - system_site_packages: False
