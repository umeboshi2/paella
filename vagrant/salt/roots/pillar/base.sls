# -*- mode: yaml -*-


# The server ip is configurable.  The only places where
# you should have to configure and refrence the paella_server_ip
# variable is in this file.  The variable is used in the dhcpd and
# livebuild namespaces below.  The 'n3' variable below is
# only used in the dhcpd namespace below, and isn't truly
# necessary, but handy for testing.
<% n3 = 5 %>
<% paella_server_ip = '10.0.%d.1' % n3 %>

# This ip can also be found in dhcpd.sls and livebuild.sls
# If this value is changed, the corresponding variables in 
# those files need to be changed as well.
paella_server_ip:  ${paella_server_ip}

dhcpd:
  paella_subnet: 10.0.${n3}.0
  paella_netmask: 255.255.255.128
  paella_subnet_range_low_ip: 10.0.${n3}.20
  paella_subnet_range_high_ip: 10.0.${n3}.126
  #paella_subnet_domain: pillar['localnet']['domain']
  # need to reference pillar data within pillar
  paella_subnet_domain: 'paellanet'
  paella_subnet_ddns_domain: 'paellanet'
  paella_subnet_dns_servers: ${paella_server_ip}
  paella_subnet_routers: ${paella_server_ip}
  paella_subnet_tftp_server: ${paella_server_ip}


  
# The default is to operate in a vagrant virtual machine.
# In order for some ofthe states to work, the paella_user 
# must be able to use sudo without a password.
paella_user: vagrant
paella_group: vagrant


# If you already have a local mirror, set this to True
# THIS DOESN'T WORK YET. KEEP IT SET TO FALSE.
paella_use_local_mirror: False

paella_localmirror_mainrepo: http://cypress/debrepos/debian
paella_localmirror_secrepo: http://cypress/debrepos/security
paella_localmirror_archive_key: http://cypress/debrepos/debrepos.gpg
paella_localmirror_archive_key_id: C4B08740

# after everything has been downloaded and verified,
# setting this option to false will make calls to 
# highstate much quicker.
#paella_enable_software_download_states: True
paella_enable_software_download_states: True

# The Windows 7 and WAIK iso files are
# currently over 4 gigabytes in size, and
# an amd64 iso would add over two more.
# Unless you already have these files, it will
# be necessary to set this value to True to 
# download and verify them.

# ALSO, be aware that these files are stored
# in /var/cache/salt.... as well as outside 
# the virtual machine in /vagrant/vagrant/cache
# You may want to rm those files, or destroy
# and recreate the virtual machine.
paella_really_download_or_check_the_large_iso_files: False


paella_virtualenv_basedir: /var/lib/paella




node_version: 0.10.25

  
livebuild:
  base_directory: /var/cache/netboot/livebuild
  distribution: wheezy
  parent_distribution: wheezy
  architectures_i386: i386
  architectures_amd64: amd64
  mirror: http://ftp.us.debian.org/debian
  mirror_security: http://security.debian.org/
  bootloader: syslinux
  binary_images: netboot
  net_root_server: ${paella_server_ip}
  net_root_filesystem: nfs
  net_root_path: /srv/debian-live
  apt_key: http://localhost/debrepos/paella.gpg
  local_mirror: http://localhost/debrepos/debian
  local_security_mirror: http://localhost/debrepos/security
  lan_mirror: http://${paella_server_ip}/debrepos/debian
  lan_security_mirror: http://${paella_server_ip}/debrepos/security
  enable_xfce_desktop: True






