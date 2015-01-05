# -*- mode: yaml -*-
{% set parent_path = '/vagrant/vagrant/cache' %}

internet_resources:
  clonezilla_iso:
    source: http://downloads.sourceforge.net/project/clonezilla/clonezilla_live_stable/2.2.2-37/clonezilla-live-2.2.2-37-i686-pae.iso
    source_hash: sha256=e057437c82127dc7188b5b52b012c5476b6e73a31863c6232874e52fac097e71
    name: {{ parent_path }}/clonezilla-i386.iso

