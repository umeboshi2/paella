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


    
    - reprepro
    - saltmaster
    # FIXME I tried to use include
    # but dicts are overwritten rather than
    # merged as in top file.
    - internet-resources.wheezy
    - internet-resources.jessie

    - local-overrides