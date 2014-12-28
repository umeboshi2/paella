# -*- mode: yaml -*-

paella-webclient-npm-install:
  cmd.run:
    - unless: test -d /vagrant/client/node_modules
    - name: npm install
    - user: vagrant
    - cwd: /vagrant/client

paella-webclient-bower-install:
  cmd.run:
    - unless: test -d /vagrant/client/bower_components
    - name: bower install
    - user: vagrant
    - cwd: /vagrant/client
    - env:
        CI: 'true'
    - require:
        - cmd: paella-webclient-npm-install

      
paella-webclient-generate-css:
  cmd.run:
    # FIXME this test is not good enough
    - unless: test -r /vagrant/client/sass/screen-PaellaDefault.scss
    - name: python scripts/generate-scss.py
    - user: vagrant
    - cwd: /vagrant/client

paella-webclient-prepare-bower-components:
  cmd.run:
    - unless: test -d /vagrant/client/components
    - name: python scripts/prepare-bower-components.py
    - user: vagrant
    - cwd: /vagrant/client
    - require:
        - cmd: paella-webclient-bower-install


paella-webclient-run-grunt:
  cmd.run:
    - unless: test -d /vagrant/client/stylesheets
    - name: grunt compass:compile && grunt coffee:compileWithMaps
    - user: vagrant
    - cwd: /vagrant/client
    - require:
        - cmd: paella-webclient-prepare-bower-components

  