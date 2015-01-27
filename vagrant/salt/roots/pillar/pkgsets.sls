# -*- mode: yaml -*-
{% from 'bvars.jinja' import paella %}
{% set mswin = paella.install_mswindows_machines %}


pkgsets:
  paella:
    basic-tools: True
    devpackages: True
    python-dev: True
    python-libdev: True
    misc-packages: True

