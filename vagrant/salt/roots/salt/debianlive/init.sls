# -*- mode: yaml -*-

live-build:
  pkg:
    - latest


/srv/livebuild:
  file.directory:
    - makedirs: True


# This is modified to accept a url with the _KEY variable
/usr/lib/live/build/bootstrap_archive-keys:
  file.managed:
    - source: salt://debianlive/bootstrap_archive-keys
    - user: root
    - group: root
    - mode: 755


