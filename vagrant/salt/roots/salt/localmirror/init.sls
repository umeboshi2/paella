# -*- mode: yaml -*-
{% set pget = salt['pillar.get'] %}

vagrant_defaults = """\
deb http://mirrors.kernel.org/debian wheezy main
deb-src http://mirrors.kernel.org/debian wheezy main

deb http://security.debian.org/ wheezy/updates main
deb-src http://security.debian.org/ wheezy/updates main

# wheezy-updates, previously known as 'volatile'
deb http://mirrors.kernel.org/debian wheezy-updates main
deb-src http://mirrors.kernel.org/debian wheezy-updates main
"""



# FIXME This isn't working yet
{% set use_localmirror = pget('paella_use_local_mirror') %}

{% if use_localmirror: %}
{% for disabled in pget('disabled_pkgrepos', []): %}
disabled-{{ disabled }}:
  pkgrepo.absent:
    - name: disabled['name']
{% endif %}

{% set archive_key = pget('paella_localmirror_archive_key') %}
{% set archive_key_id = pillar('paella_localmirror_archive_key_id') %}
sources-list:
  file.managed:
    - name: /etc/apt/sources.list
    - source: salt://localmirror/sources.list
    - template: mako

add-localmirror-key:
  cmd.run:
    - unless: apt-key list | grep {{ archive_key_id }}
    - name: wget -q -O - {{ archive_key }} | apt-key add - && apt-get -y update
    
{% endif %}

