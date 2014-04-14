# -*- mode: yaml -*-

<% user = pillar['paella_user'] %>
<% group = pillar['paella_group'] %>


# saltrepos
/srv/debrepos/salt/conf:
  file.directory:
    - makedirs: True

/srv/debrepos/salt/conf/updates:
  file.managed:
    - source: salt://debrepos/salt-updates

/srv/debrepos/salt/conf/distributions:
  file.managed:
    - source: salt://debrepos/salt-dist

saltrepos-ready:
  cmd.run:
    - name: echo "saltrepos-ready"
    - user: ${user}
    - group: ${group}
    - cwd: /srv/debrepos/salt
    - requires:
      - file: /srv/debrepos/salt/conf
      - file: /srv/debrepos/salt/conf/updates
      - file: /srv/debrepos/salt/conf/distributions

update-saltrepos:
  cmd.run:
    - name: reprepro -VV --noskipold update
    - unless: test -d /srv/debrepos/salt/db
    - user: ${user}
    - group: ${group}
    - cwd: /srv/debrepos/salt
    - requires:
      - cmd: saltrepos-ready
