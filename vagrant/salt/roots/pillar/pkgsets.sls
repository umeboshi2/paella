# -*- mode: yaml -*-
{% from 'config.jinja' import paella %}
{% set mswin = paella.install_mswindows_machines %}

system:
  toolsets_combined: true
  toolsets:
    python-libdev-jessie: true
    base-tools: true
    system-monitor-tools: true
    base-development-tools: true
    base-debian-dev-tools: true
    base-python-development: true
    default-text-packages: true
    
    

# FIXME: remove all pkgsets

#pkgsets:
#  paella:
#    basic-tools: True
#    devpackages: True
#    python-dev: True
#    python-libdev: True
#    misc-packages: True

