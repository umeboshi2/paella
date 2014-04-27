# -*- mode: yaml -*-

# The default is to operate in a vagrant virtual machine.
# In order for some ofthe states to work, the paella_user 
# must be able to use sudo without a password.
paella_user: vagrant
paella_group: vagrant


# This ip can also be found in dhcpd.sls and livebuild.sls
# If this value is changed, the corresponding variables in 
# those files need to be changed as well.
paella_server_ip:  10.0.4.1


# If you already have a local mirror, set this to True
# THIS DOESN'T WORK YET. KEEP IT SET TO FALSE.
paella_use_local_mirror: False

paella_localmirror_mainrepo: http://cypress/debrepos/debian
paella_localmirror_secrepo: http://cypress/debrepos/security
paella_localmirror_archive_key: http://cypress/debrepos/debrepos.gpg
paella_localmirror_archive_key_id: C4B08740

#paella_enable_samba: False
paella_enable_samba: True

# after everything has been downloaded and verified,
# setting this option to false will make calls to 
# highstate much quicker.
#paella_enable_software_download_states: True
paella_enable_software_download_states: True


# nu2_mirror CANNOT end with a trailing /
#nu2_mirror: http://ftp.rz.tu-bs.de/pub/mirror/www.nu2.nu/nu2files
#nu2_mirror: http://securitywonks.org/n2u/mirrorfiles
nu2_mirror: ftp://dl.xs4all.nl/pub/mirror/nu2files
