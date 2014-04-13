# -*- mode: yaml -*-

postgresql-support-packages:
  pkg.installed:
    - pkgs:
      - postgresql-contrib

/etc/postgresql/9.1/main/pg_hba.conf:
  file.managed:
    - source: salt://postgresql/pg_hba.conf
    - user: postgres
    - group: postgres
    - mode: 640


postgresql:
  pkg.installed:
    - name: postgresql
    - requires:
      - pkg: postgresql-support-packages

  service:
    - name: postgresql
    - running
    - watch:
      - file: /etc/postgresql/9.1/main/pg_hba.conf

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

