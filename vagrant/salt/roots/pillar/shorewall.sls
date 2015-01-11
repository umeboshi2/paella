# -*- mode: yaml -*-

shorewall:
  ip_forwarding: 'On'
  shorewall_package: shorewall-init
  config_type: double
  startup: true
  interfaces:
    - name: net
      iface: eth0
      options: dhcp,tcpflags,nosmurfs,routefilter,logmartians,sourceroute=0
    - name: loc
      iface: eth1
      options: tcpflags,nosmurfs,routefilter,logmartians
  masq:
    - iface: eth0
      sources:
        - 10.0.4.0/24
  # policies
  lan_access_internet_policy: true
  # lan host accepts all traffic
  # this should always be false, unless
  # testing firewall.  use the macros
  # to select the services provided by
  # the firewall.
  firewall_is_lan_host: true
  firewall_generates_traffic: true
  firewall_accepts_net: true
  
  #loc_macros:
  #  - DNS
  #  - DHCP
  #  - TFTP
  net_macros:
    - SSH
    
    
  #rules:
  #  - name: accept_dns_loc2fw
  #    action: DNS(ACCEPT)
  #    src: loc
  #    dest: $FW
  #  - name: accept_salt_fw2net
  #    action: SaltMaster(ACCEPT)
  #    src: $FW
  #    dest: net
      
      