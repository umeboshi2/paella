# -*- mode: yaml -*-

<% user = pillar['paella_user'] %>
<% group = pillar['paella_group'] %>

include:
  - debrepos.base
  - debrepos.keys
  - debrepos.mainrepos
  - debrepos.saltrepos
  - debrepos.secrepos
  - debrepos.paellarepos

debrepos-ready:
  cmd.run: 
    - name: echo "debrepos-ready"
    - require:
      - sls: debrepos.base
      - sls: debrepos.keys
      - sls: debrepos.mainrepos
      - sls: debrepos.saltrepos
      - sls: debrepos.secrepos
      - sls: debrepos.paellarepos
      
      