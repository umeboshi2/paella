# -*- mode: yaml -*-
{% set pget = salt['pillar.get'] %}

#vagrant_defaults = """\
#deb http://mirrors.kernel.org/debian wheezy main
#deb-src http://mirrors.kernel.org/debian wheezy main
#
#deb http://security.debian.org/ wheezy/updates main
#deb-src http://security.debian.org/ wheezy/updates main
#
## wheezy-updates, previously known as 'volatile'
#deb http://mirrors.kernel.org/debian wheezy-updates main
#deb-src http://mirrors.kernel.org/debian wheezy-updates main
#"""



# FIXME This isn't working yet
{% set use_localmirror = pget('paella:use_local_mirror_for_vagrant') %}

{% if use_localmirror: %}
{% for disabled in pget('disabled_pkgrepos', []): %}
{% set data = pget('disabled_pkgrepos')[disabled] %}
disabled-{{ disabled }}:
  pkgrepo.absent:
    - name: {{ data['name'] }}
{% endfor %}

{% for enabled in pget('enabled_pkgrepos', []): %}
{% set data = pget('enabled_pkgrepos')[enabled] %}
enabled-{{ enabled }}:
  pkgrepo.managed:
    - name: {{ data['name'] }}
    - key_url: {{ data['key_url'] }}
{% endfor %}
    
{% endif %}

