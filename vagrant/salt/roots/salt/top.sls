# -*- mode: yaml -*-

base:
  'paella':
    - localmirror
    - default
    - files
    - squid
    - debrepos
    - saltmaster
    - paella-client
    - netboot
    - mainserver
    %if pillar['paella_enable_samba']:
    - samba
    %endif

