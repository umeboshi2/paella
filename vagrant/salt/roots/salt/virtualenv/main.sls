# -*- mode: yaml -*-
{% set pget = salt['pillar.get'] %}
{% set user = pget('paella:paella_user', 'vagrant') %}
{% set group = pget('paella:paella_group', 'vagrant') %}

include:
  - default.pkgsets


# FIXME
# I'm not sure it is necessary to prepare the pip.conf file for vagrant user.
# If it is necessary, I have forgotten why.
vagrant-pip-config:
  file.managed:
    - name: /home/{{ user }}/.pip/pip.conf
    - source: salt://virtualenv/pip.conf
    - user: {{ user }}
    - makedirs: True

{% set basedir = pget('paella:virtualenv_basedir') %}
virtualenv-basedir:
  file.directory:
    - name: {{ basedir }}
    - makedirs: True
    - user: {{ user }}
    - group: {{ group }}
    - mode: 2775


# This is the virtualenv used to gather the driverpacks      
get-driverpacks-virtualenv:
  virtualenv.managed:
    - name: {{ basedir }}/dp-venv
    - system_site_packages: False
    - user: {{ user }}
    - requirements: salt://driverpacks/requirements.txt
    - require:
      - file: virtualenv-basedir


# This is the virtualenv that the paella server needs
mainserver-virtualenv:
  virtualenv.managed:
    - name: {{ pget('paella:virtualenv_basedir') }}/venv
    - system_site_packages: False
    - user: {{ user }}
    - requirements: salt://mainserver/requirements.txt
    - require:
      - file: virtualenv-basedir

halite-virtualenv:
  virtualenv.managed:
    - name: {{ pget('paella:virtualenv_basedir') }}/venv
    - system_site_packages: False
    - user: {{ user }}
    - requirements: salt://mainserver/requirements.txt
    - require:
      - file: virtualenv-basedir
  

# This looks funky, but it happens to be the only way known
# to easily put python packages hosted in git repos in the
# virtualenv's.
#<% import os %>
#<% basedir = pillar['paella_virtualenv_basedir'] %>
#%for repo in ['trumpet', 'debrepos']:
# These states only exist if the symlink doesn't exist
# in the virtualenv.
#%if not os.path.isfile(os.path.join(basedir, 'venv/lib/python2.7/site-packages/%s.egg-link' % repo)):
#mainserver-virtualenv-${repo}-requirement:
#  pip.installed:
#    - name: ${repo}
#    - user: ${pillar['paella_user']}
#    - bin_env: ${os.path.join(basedir, 'venv')}
#    - editable: git+https://github.com/umeboshi2/${repo}.git#egg=${repo}
#    - require:
#        - virtualenv: mainserver-virtualenv
#%endif
#%endfor
