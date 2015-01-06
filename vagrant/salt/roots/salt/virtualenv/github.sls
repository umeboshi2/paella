#!pydsl
# -*- mode: python -*-
import os
basedir = __pillar__['paella']['virtualenv_basedir']
user = __pillar__['paella']['paella_user']

for repo in ['trumpet', 'debrepos']:
    basename = 'venv/lib/python2.7/site-packages/%s.egg' % repo
    if not os.path.isfile(os.path.join(basedir, basename)):
        sid = 'mainserver-virtualenv-%s-requirement' % repo
        editable = 'git+https://github.com/umeboshi2/%s.git#egg=%s' % (repo, repo)
        requires = [dict(virtualenv='mainserver-virtualenv')]
        pipreq = state(sid)
        pipreq.pip('installed',
                   name=repo,
                   user=user,
                   bin_env=os.path.join(basedir, 'venv'),
                   editable=editable,
                   requires=requires)
                          


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
