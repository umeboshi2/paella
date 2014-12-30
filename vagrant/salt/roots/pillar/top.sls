# -*- mode: yaml -*-

base:
  '*':
    - base
    - localnet
    - default-ports
    - reprepro
    - saltmaster
    - internet-resources
    # FIXME I tried to use include
    # but dicts are overwritten rather than
    # merged as in top file.
    - internet-resources.wheezy
    - internet-resources.jessie
    