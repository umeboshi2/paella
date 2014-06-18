# -*- mode: yaml -*-

#####################################

# winbuilder
# 

include:
  - netboot

test-mkenv-batch-script:
  file.managed:
    - name: /srv/shares/incoming/mkenv.bat
    - source: salt://winbuilder/mkenv.bat

test-install-python-script:
  file.managed:
    - name: /srv/shares/incoming/install.py
    - source: salt://winbuilder/install.py


