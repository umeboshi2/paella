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
    - shorewall
    
    - reprepro
    - saltmaster

    - local-overrides