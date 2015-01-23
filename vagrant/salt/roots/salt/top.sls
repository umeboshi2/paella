# -*- mode: yaml -*-
{% set pget = salt['pillar.get'] %}
base:
  'paella':
    {%- for sls in pget('paella:top_states', ['default']) %}
    - {{ sls }}
    {% endfor -%}
