# -*- mode: yaml -*-

reprepro:
  parent_directory: /srv/debrepos
  distribution: wheezy
  #architectures: i386 amd64
  architectures: amd64
  mirror: http://ftp.us.debian.org/debian
  mirror_security: http://security.debian.org/
  saltrepos:
    debdists:
      #- squeeze
      - wheezy
      #- jessie
    saltbranches:
      - 2014-07
      #- 2014-01
      





