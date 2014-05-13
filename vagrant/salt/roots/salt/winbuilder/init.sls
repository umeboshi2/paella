# -*- mode: yaml -*-

#####################################

# winbuilder
# 

include:
  - netboot
  - samba

test-mkenv-batch-script:
  file.managed:
    - name: /srv/shares/incoming/mkenv.bat
    - source: salt://winbuilder/mkenv.bat


