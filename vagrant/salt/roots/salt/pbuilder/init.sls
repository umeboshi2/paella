# -*- mode: yaml -*-

include:
  - default

# it looks like pbuilder may be
# required to effectively build
# wimlib for both i386 and amd64
wimlib-build-depends-extra:
  pkg.installed:
    - pkgs:
      - pbuilder


