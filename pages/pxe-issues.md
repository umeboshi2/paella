# [Paella](#)

### PXE Issues

Netbooting varies from machine to machine.  There are many machines that will 
not boot from the network unless a key, like F12, is pressed during the 
preboot.  

Other machines will readily boot from the network at first option.  I intend 
for paella to be flexible enough to handle these situations.  The default 
pxe config file will default to booting from the first hard drive 
automatically after a ten second delay.  A machine that boots from the 
network by default, or as the first boot device, will effectively 
default to booting from their first hard drive.


