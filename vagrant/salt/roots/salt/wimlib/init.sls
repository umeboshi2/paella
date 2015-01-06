# -*- mode: yaml -*-
{% set pget = salt['pillar.get'] %}
{% set user = pget('paella_user') %}
{% set group = pget('paella_group') %}

#####################################

include:
  - wimlib.builder
