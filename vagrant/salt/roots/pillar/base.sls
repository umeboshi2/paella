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

