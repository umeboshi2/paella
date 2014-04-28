# Notes

## Rearranging states


##############
default first

packages, alternatives
##############################

Try to get all upstream debian packages in default.sls

Most sls files will depend on default


All packages from debian should be installed before debrepos
is created and local package list generated for partial mirror.

######################################

debrepos

create and update debrepos

#####################################

upstream files

get upstream files such as win7.iso and aik.iso
get debian installer files for netboot

get upstream git repos

files in salt

many files can be placed on filesystem now

#####################################


build local packages

build paella-client and wimlib
upload to paella package repo

########################################

build live image (depends paella-client)

#######################################

mainserver virtualenv

##############################

build winpe image

###########################


basic services

shorewall
dhcpd
bind
apache
tftpd
postgresql
saltmaster
samba
squid (need to remove squid?)


