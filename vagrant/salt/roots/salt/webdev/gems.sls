# -*- mode: yaml -*-

compass:
  gem.installed
sassy-buttons:
  gem.installed
  
execjs:
  gem.installed:
    - version: 2.3.0
  
bootstrap-sass:
  gem.installed:
    - version: 3.3.3
    - require:
      - gem: execjs

compass-ui:
  gem.installed
