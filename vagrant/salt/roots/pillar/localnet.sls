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


network:
  interfaces:
    - name: eth1
      proto: static
      ipaddr: 10.0.4.1
      netmask: 255.255.255.0
      
dhclient:
  supersede:
    domain-name: '"paellanet"'
  prepend:
    domain-name-servers: 127.0.0.1
    
binddns:
  lookup:
    config:
      named_conf:
        controls:
          - 'inet 127.0.0.1 port 953 allow { 127.0.0.1; } keys { "rndc-key"; };'
    dnssec_validation: 'no'
  zones:
    - create_db_only: true
      name: paellanet
      soa: paella
      additional:
        - allow-update { key "rndc-key"; }
      records:
        - owner: paella
          ttl: 86400
          class: A
          data: 10.0.4.1
    - create_db_only: true
      name: 4.0.10.in-addr.arpa
      soa: paella
      additional:
        - allow-update { key "rndc-key"; }
      records:
        - owner: 1
          ttl: 86400
          class: PTR
          data: paella.paellanet.
  
iscdhcp: 
  listen_interfaces:
    - eth1
  lookup:
    config:
      subnets:
        manage: true
      pxe_subnets:
        manage: true
      dhcpd:
        options:
          - domain-name "paellanet"
          - domain-name-servers 10.0.4.1
        zones:
          - name: paellanet.
            primary: 127.0.0.1
            key: rndc-key
          - name: 4.0.10.in-addr.arpa.
            primary: 127.0.0.1
            key: rndc-key
            
        file_prepend: |
          include "/etc/bind/rndc.key";
  pxe_subnets:
    - network: 10.0.4.0
      netmask: 255.255.255.0
      range: '10.0.4.20 10.0.4.126'
      routers: 10.0.4.1
      ddns_domainname: paellanet
      ddns_updates: 'on'
      do_forward_updates: 'on'
      tftp_server: 10.0.4.1
      pxelinux: pxelinux.0
      gpxelinux: gpxelinux.0



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


