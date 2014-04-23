# Paella Server

The paella server is a [Pyramid](http://www.pylonsproject.org/) web 
server that has a simple
[REST](http://en.wikipedia.org/wiki/Representational_state_transfer) 
interface for handling the machines.  The web server is also responsible 
for serving the preseed files and configuration scripts that are 
specific to the machine being installed or configured.  At this time, 
the paella server *must* have write access to the pxelinux.cfg directory 
in the directory that contains the pxelinux.0 file mentioned by the 
dhcp server.  This is currently hardcoded to /var/lib/tftpboot/pxelinux.cfg 
and needs to be adapted.



