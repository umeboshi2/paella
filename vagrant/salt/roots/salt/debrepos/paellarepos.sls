# -*- mode: yaml -*-

<% user = pillar['paella_user'] %>
<% group = pillar['paella_group'] %>


# saltrepos
/srv/debrepos/paella/conf:
  file.directory:
    - makedirs: True

/srv/debrepos/paella/conf/distributions:
  file.managed:
    - source: salt://debrepos/repos/paella/distributions
    - template: mako

paellarepos-ready:
  cmd.run:
    - name: echo "paellarepos-ready"
    - user: ${user}
    - cwd: /srv/debrepos/paella
    - requires:
      - file: /srv/debrepos/paella/conf
      - file: /srv/debrepos/paella/conf/distributions

export-paellarepos:
  cmd.run:
    - name: reprepro -VV --noskipold export
    - unless: test -d /srv/debrepos/paella/db
    - user: ${user}
    - cwd: /srv/debrepos/paella
    - requires:
      - cmd: paellarepos-ready
