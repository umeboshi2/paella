# -*- mode: yaml -*-
{% from 'config.jinja' import paella %}
include:
  - internet-resources.main
  {% for dist in paella.debian_releases %}
  - internet-resources.{{ dist }}
  {% endfor %}
  {% for dist in paella.ubuntu_releases %}
  - internet-resources.{{ dist }}
  {% endfor %}
  {% if paella.install_mswindows_machines %}
  - internet-resources.windows-install-files
  - internet-resources.windows-iso-files
  {% endif %}
  {% if paella.get_extra_iso_files %}
  - internet-resources.more-iso-files
  {% endif %}
  