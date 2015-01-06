# -*- mode: yaml -*-
{% from 'bvars.jinja' import paella_user %}
{% from 'bvars.jinja' import paella_group %}
{% from 'bvars.jinja' import n3, paella_server_ip %}


localnet:
  domain: paellanet
  default-ports:
    mountd: 50919
    statd: 50920
    nfs: 2049
    bootpc: 68
    bootps: 67
    gkrellmd: 19150
    portmap: 111
    manage_sieve: 2020

paella:
  # The server ip is configurable.  The only places where
  # you should have to configure and refrence the paella_server_ip
  # variable is in this file.  The variable is used in the dhcpd and
  # livebuild namespaces below.  The 'n3' variable below is
  # only used in the dhcpd and bind namespaces below, and isn't truly
  # necessary, but handy for testing.
  paella_server_ip:  {{ paella_server_ip }}
  
  bind:
    in-addr: {{ n3 }}.0.10
  dhcpd:
    paella_subnet: 10.0.{{ n3 }}.0
    paella_netmask: 255.255.255.128
    paella_subnet_range_low_ip: 10.0.{{ n3 }}.20
    paella_subnet_range_high_ip: 10.0.{{ n3 }}.126
    #paella_subnet_domain: pillar['localnet']['domain']
    # need to reference pillar data within pillar
    paella_subnet_domain: 'paellanet'
    paella_subnet_ddns_domain: 'paellanet'
    paella_subnet_dns_servers: {{ paella_server_ip }}
    paella_subnet_routers: {{ paella_server_ip }}
    paella_subnet_tftp_server: {{ paella_server_ip }}


  # If you already have a local mirror, set this to True
  use_local_mirror_for_vagrant: False

