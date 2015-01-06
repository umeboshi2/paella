# -*- mode: yaml -*-
{% from 'bvars.jinja' import paella_user %}
{% from 'bvars.jinja' import paella_group %}
{% from 'bvars.jinja' import n3, paella_server_ip %}

paella:
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

