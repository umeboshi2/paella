# -*- mode: yaml -*-
{% from 'bvars.jinja' import paella %}
include:
  - internet-resources.main
  - internet-resources.wheezy
  - internet-resources.jessie
  - internet-resources.trusty
  {% if paella.install_mswindows_machines %}
  - internet-resources.windows-install-files
  - internet-resources.windows-iso-files
  {% endif %}
  - internet-resources.more-iso-files
  