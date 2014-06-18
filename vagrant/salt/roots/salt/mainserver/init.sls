# -*- mode: yaml -*-

include:
  - apache
  - virtualenv
  - postgresql

extend:
  apache-service:
    service:
      - watch:
        - file: paella-apache-config
        - file: paella-wsgi-script



paella-apache-config:
  file.managed:
    - name: /etc/apache2/conf.d/paella
    - source: salt://mainserver/paella-apache-config
    - template: mako


paella-wsgi-script:
  file.managed:
    - name: /etc/apache2/paella.wsgi
    - source: salt://mainserver/paella-wsgi-script
    - user: root
    - group: root
    - mode: 755


# this command is always run
# this command checks if paella is in `pip freeze` 
# before executing, but this can't be done easily
# with the unless paramater due to the need for 
# the virtualenv requirement.
setup-paella:
  cmd.script:
    - unless: false
    - requires:
      - virtualenv: mainserver-virtualenv
      - sls: postgresql
    - source: salt://scripts/setup-paella.sh
    - user: ${pillar['paella_user']}
    - template: mako
    


# FIXME This command also should require
# that the postgres server is running.
setup-paella-database:
  cmd.script:
    - unless: psql --tuples-only -c 'SELECT name FROM models;' paella | grep '^ one$'
    - requires:
      - cmd: setup-paella
    - source: salt://scripts/setup-paella-database.sh
    - user: postgres
    - template: mako

