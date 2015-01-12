# -*- mode: yaml -*-
{% from 'bvars.jinja' import paella_user %}
{% from 'bvars.jinja' import paella_group %}
{% from 'bvars.jinja' import paella_server_ip %}

paella:  
  # The default is to operate in a vagrant virtual machine.
  # In order for some ofthe states to work, the paella_user 
  # must be able to use sudo without a password.
  paella_user: {{ paella_user }}
  paella_group: {{ paella_group }}

  # If you already have a local mirror, set this to True
  use_local_mirror_for_vagrant: False

  debian_archive_keyring_versions:
    wheezy: 2014.1~deb7u1
    jessie: 2014.3
  virtualenv_basedir: /var/lib/paella
  node_version: 0.10.25
  
    


paella_virtualenv_basedir: /var/lib/paella




node_version: 0.10.25
