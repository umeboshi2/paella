# -*- mode: yaml -*-

base:
  '*':
    - base
    - default-ports
    - pkgsets
    - internet-resources
    - localnet
    - samba
    - schroot
    - livebuild

    
    - reprepro
    - saltmaster

    - local-overrides