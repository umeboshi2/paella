# -*- mode: yaml -*-

include:
  - postgresql.base

# FIXME
# We really need to make a password for the dbadmin user
# and fix the pg_hba.conf file as well.
  
/etc/postgresql/9.1/main/pg_hba.conf:
  file.managed:
    - source: salt://postgresql/pg_hba.conf
    - user: postgres
    - group: postgres
    - mode: 640

# FIXME      
# For debug and development purposes, the
# paella server is accepting db connections
# on the second network interface.  This should
# not be done in production.
/etc/postgresql/9.1/main/postgresql.conf:
  file.managed:
    - source: salt://postgresql/postgresql.conf
    - user: postgres
    - group: postgres
    - mode: 644
    - template: jinja

      
postgresql-service:
  service.running:
    - name: postgresql
    - requires:
      - pkg: postgresql-package
    - watch:
      - file: /etc/postgresql/9.1/main/pg_hba.conf
      - file: /etc/postgresql/9.1/main/postgresql.conf

paella_database_user:
  postgres_user.present:
    - name: dbadmin
    - createdb: true
    - createruser: true
    - superuser: true
    - user: postgres
      
paella_database:
  postgres_database.present:
    - name: paella
    - owner: dbadmin
    - user: postgres
      
{#

pg_createuser_dbadmin:
  cmd.run:
    - name: createuser --superuser --createdb --createrole dbadmin
    - unless: psql --tuples-only -c 'SELECT rolname FROM pg_catalog.pg_roles;' | grep '^ dbadmin$'
    - user: postgres
    - requires:
      - service: postgresql
        
pg_createdb_paella:
  cmd.run:
    - name: createdb -O dbadmin paella
    - unless: psql -ltA | grep '^paella'
    - user: postgres

#}

        
