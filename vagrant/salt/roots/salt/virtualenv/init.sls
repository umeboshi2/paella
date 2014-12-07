# -*- mode: yaml -*-

include:
  - default


vagrant-pip-config:
  file.managed:
    - name: /home/${pillar['paella_user']}/.pip/pip.conf
    - source: salt://virtualenv/pip.conf
    - user: ${pillar['paella_user']}
    - makedirs: True


virtualenv-basedir:
  file.directory:
    - name: ${pillar['paella_virtualenv_basedir']}
    - makedirs: True
    - group: ${pillar['paella_group']}
    - mode: 2775


get-driverpacks-virtualenv:
  virtualenv.managed:
    - name: ${pillar['paella_virtualenv_basedir']}/dp-venv
    - system_site_packages: False
    - user: ${pillar['paella_user']}
    - requirements: salt://driverpacks/requirements.txt
    - require:
      - file: virtualenv-basedir



mainserver-virtualenv:
  virtualenv.managed:
    - name: ${pillar['paella_virtualenv_basedir']}/venv
    - system_site_packages: False
    - user: ${pillar['paella_user']}
    - requirements: salt://mainserver/requirements.txt
    - require:
      - file: virtualenv-basedir

<% import os %>
<% basedir = pillar['paella_virtualenv_basedir'] %>
%for repo in ['trumpet', 'debrepos']:
%if not os.path.isfile(os.path.join(basedir, 'venv/lib/python2.7/site-packages/%s.egg-link' % repo)):
${repo}-requirement:
  pip.installed:
    - name: ${repo}
    - user: ${pillar['paella_user']}
    - bin_env: ${os.path.join(basedir, 'venv')}
    - editable: git+https://github.com/umeboshi2/${repo}.git#egg=${repo}
    - require:
        - virtualenv: mainserver-virtualenv
%endif
%endfor
