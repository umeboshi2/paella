# -*- mode: yaml -*-

include:
  - postgresql.base

/etc/postgresql/9.1/main/pg_hba.conf:
  file.managed:
    - source: salt://postgresql/pg_hba.conf
    - user: postgres
    - group: postgres
    - mode: 640

/etc/postgresql/9.1/main/postgresql.conf:
  file.managed:
    - source: salt://postgresql/postgresql.conf
    - user: postgres
    - group: postgres
    - mode: 644

postgresql-service:
  service.running:
    - name: postgresql
    - requires:
      - pkg: postgresql-package
    - watch:
      - file: /etc/postgresql/9.1/main/pg_hba.conf
      - file: /etc/postgresql/9.1/main/postgresql.conf

pg_createuser_dbadmin:
  cmd.run:
    - name: createuser --superuser --createdb --createrole dbadmin
    - unless: psql --tuples-only -c 'SELECT rolname FROM pg_catalog.pg_roles;' | grep '^ dbadmin$'
    - user: postgres
    - requires:
      - service: postgresql

pg_createuser_paella:
  cmd.run:
    - name: createuser --no-superuser --no-createdb --no-createrole paella
    - unless: psql --tuples-only -c 'SELECT rolname FROM pg_catalog.pg_roles;' | grep '^ paella$'
    - user: postgres
    - requires:
      - service: postgresql

pg_createdb_paella:
  cmd.run:
    - name: createdb -O dbadmin paella
    - unless: psql -ltA | grep '^paella'
    - user: postgres

