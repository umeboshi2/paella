# -*- mode: yaml -*-
{% set pget = salt['pillar.get'] %}
{% set user = pget('paella:paella_user', 'vagrant') %}
{% set group = pget('paella:paella_group', 'vagrant') %}
{% set oscodename = salt['grains.get']('oscodename') %}
{% if oscodename == 'wheezy': %}
{% set apache_confdir = '/etc/apache2/conf.d' %}
{% else %}
{% set apache_confdir = '/etc/apache2/conf-available' %}
{% endif %}

include:
  - apache
  - virtualenv
  - postgres
  - webdev

{% if pget('paella:install_rabbitmq', False) %}
rabbitmq-packages:
  pkg.installed:
    - pkgs:
      - rabbitmq-server
{% endif %}

  
extend:
  apache:
    service:
      - watch:
        - file: paella-apache-config
        - file: paella-wsgi-script
        - file: paella-pyramid-settings-file
          


paella-apache-config:
  file.managed:
    - name: {{ apache_confdir}}/paella
    - source: salt://mainserver/paella-apache-config
    - template: mako


paella-wsgi-script:
  file.managed:
    - name: /etc/apache2/paella.wsgi
    - source: salt://mainserver/paella-wsgi-script
    - user: root
    - group: root
    - mode: 755

paella-pyramid-settings-file:
  file.managed:
    - name: /etc/apache2/paella-dev.ini
    - source: salt://mainserver/paella-dev.ini
    - template: jinja
      
      
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
      - sls: postgres
    - source: salt://scripts/setup-paella.sh
    - user: {{ user }}
    - template: jinja
    


# FIXME This command also should require
# that the postgres server is running.
setup-paella-database:
  cmd.script:
    - unless: psql --tuples-only -c 'SELECT name FROM models;' paella | grep '^ one$'
    - requires:
      - cmd: setup-paella
    - source: salt://scripts/setup-paella-database.sh
    - user: postgres
    - template: jinja

