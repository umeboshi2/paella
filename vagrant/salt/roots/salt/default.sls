# -*- mode: yaml -*-

pager:
  alternatives.set:
    - name: pager
    - path: /usr/bin/most


screen:
  pkg:
    - latest


update_bower:
  cmd.run:
    - name: npm update -g bower
