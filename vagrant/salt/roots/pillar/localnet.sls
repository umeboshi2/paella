# -*- mode: yaml -*-
{% from 'config.jinja' import paella %}


localnet:
  domain: {{ paella.paella_subnet_domain }}
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
      ipaddr: {{ paella.paella_server_ip }}
      netmask: {{ paella.paella_subnet_netmask }}
      
dhclient:
  supersede:
    domain-name: '"{{ paella.paella_subnet_domain }}"'
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
      name: {{ paella.paella_subnet_domain }}
      soa: {{ paella.paella_hostname }}
      additional:
        - allow-update { key "rndc-key"; }
      records:
        - owner: {{ paella.paella_hostname }}
          ttl: 86400
          class: A
          data: {{ paella.paella_server_ip }}
    - create_db_only: true
      name: {{ paella.paella_subnet_in_addr }}.in-addr.arpa
      soa: paella
      additional:
        - allow-update { key "rndc-key"; }
      records:
        - owner: 1
          ttl: 86400
          class: PTR
          data: {{ paella.paella_hostname}}.{{ paella.paella_subnet_domain}}.
  
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
          - domain-name "{{ paella.paella_subnet_domain }}"
          - domain-search "{{ paella.paella_subnet_domain }}"
          - domain-name-servers {{ paella.paella_server_ip }}
        zones:
          - name: {{ paella.paella_subnet_domain}}.
            primary: 127.0.0.1
            key: rndc-key
          - name: {{ paella.paella_subnet_in_addr }}.in-addr.arpa.
            primary: 127.0.0.1
            key: rndc-key
            
        file_prepend: |
          include "/etc/bind/rndc.key";
  pxe_subnets:
    - network: {{ paella.paella_subnet_network }}
      netmask: {{ paella.paella_subnet_netmask }}
      range: '{{ paella.paella_subnet_range_low }} {{ paella.paella_subnet_range_high }}'
      routers: {{ paella.paella_server_ip }}
      ddns_domainname: {{ paella.paella_subnet_domain }}
      ddns_updates: 'on'
      do_forward_updates: 'on'
      tftp_server: {{ paella.paella_server_ip }}
      pxelinux: pxelinux.0
      gpxelinux: gpxelinux.0



paella:
  # The server ip is configurable.  The only places where
  # you should have to configure and refrence the paella_server_ip
  # variable is in this file.  The variable is used in the dhcpd and
  # livebuild namespaces below.  The 'n3' variable below is
  # only used in the dhcpd and bind namespaces below, and isn't truly
  # necessary, but handy for testing.
  paella_server_ip:  {{ paella.paella_server_ip }}
  
  bind:
    in-addr: {{ paella.paella_subnet_in_addr }}
  dhcpd:
    paella_subnet: {{ paella.paella_subnet_network }}
    paella_netmask: {{ paella.paella_subnet_netmask }}
    paella_subnet_range_low_ip: {{ paella.paella_subnet_range_low }}
    paella_subnet_range_high_ip: {{ paella.paella_subnet_range_high }}
    #paella_subnet_domain: pillar['localnet']['domain']
    # need to reference pillar data within pillar
    paella_subnet_domain: '{{ paella.paella_subnet_domain }}'
    paella_subnet_ddns_domain: '{{ paella.paella_subnet_domain }}'
    paella_subnet_dns_servers: {{ paella.paella_server_ip }}
    paella_subnet_routers: {{ paella.paella_server_ip }}
    paella_subnet_tftp_server: {{ paella.paella_server_ip }}


  # If you already have a local mirror, set this to True
  use_local_mirror_for_vagrant: False


