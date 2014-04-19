# -*- mode: yaml -*-

<% use_localmirror = pillar['paella_use_local_mirror'] %>

%if use_localmirror:

<% archive_key = pillar['paella_localmirror_archive_key'] %>
<% archive_key_id = pillar['paella_localmirror_archive_key_id'] %>
sources-list:
  file.managed:
    - name: /etc/apt/sources.list
    - source: salt://localmirror/sources.list
    - template: mako

add-localmirror-key:
  cmd.run:
    - unless: apt-key list | grep ${archive_key_id}
    - name: wget -q -O - ${archive_key} | apt-key add - && apt-get -y update
    
%endif
