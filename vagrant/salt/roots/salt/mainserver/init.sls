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

# this command is always run
# this command checks if paella is in `pip freeze` 
# before executing, but this can't be done easily
# with the unless paramater due to the need for 
# the virtualenv requirement.
setup-paella:
  cmd.script:
    - unless: false
    - requires:
      - virtualenv: /var/lib/paella/venv
    - source: salt://scripts/setup-paella.sh
    - user: ${pillar['paella_user']}


# FIXME This command also should require
# that the postgres server is running.
setup-paella-database:
  cmd.script:
    - unless: psql --tuples-only -c 'SELECT name FROM models;' paella | grep '^ one$'
    - requires:
      - cmd: setup-paella
    - source: salt://scripts/setup-paella-database.sh
    - user: postgres

