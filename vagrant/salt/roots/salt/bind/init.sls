# -*- mode: yaml -*-

include:
  - bind.base

bind-local-zone-config-file:
  file.managed:
    - name: /etc/bind/named.conf.local
    - source: salt://bind/named.conf.local
    - template: mako
    - requires:
      - pkg: bind9
    - user: root
    - group: bind
      

%for direction in ['paellanet', 'rev']:
bind-paella-zone-${direction}-file:
  file.managed:
    - name: /etc/bind/db.${direction}
    - source: salt://bind/db.${direction}
    - template: mako
    - requires:
      - pkg: bind9
    - user: root
    - group: root

%endfor
  
      
bind-service:
  service.running:
    - name: bind9
    - requires:
      - file: bind-local-zone-config-file
    - watch:
      - file: bind-local-zone-config-file


paellanet-zone-file:
  file.managed:
    - name: /etc/bind/db.paellanet
    