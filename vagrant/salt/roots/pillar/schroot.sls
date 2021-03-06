# -*- mode: yaml -*-

{% from 'config.jinja' import paella %}

schroot_sections:
  {% set nmap = dict(amd64='', i386='32') %}
  {% for dist in ['wheezy', 'jessie']: %}
  {% for arch in ['amd64', 'i386']: %}
  {# "SECTION" #}
  {{ dist }}{{ nmap[arch] }}:
    description: Debian {{ dist }} ({{ arch }})
    directory: /srv/roots/{{ dist }}-{{ arch }}
    type: directory
    users: {{ paella.paella_user }}
    root-users: {{ paella.paella_user }}
  {% endfor %}
  {% endfor %}


