# -*- mode: yaml -*-
{% set pget = salt['pillar.get'] %}
{% set user = pget('paella_user') %}
{% set group = pget('paella_group') %}

include:
  - default.pkgsets
  - virtualenv.main
  - virtualenv.github
  


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
