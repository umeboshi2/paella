# -*- mode: yaml -*-

/var/lib/paella:
  file.directory:
    - makedirs: True
    - group: ${pillar['paella_group']}
    - mode: 2775


/var/lib/paella/venv:
  virtualenv.managed:
    - system_site_packages: False
    - user: ${pillar['paella_user']}
    - requirements: salt://mainserver/requirements.txt


