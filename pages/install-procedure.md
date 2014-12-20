# [Paella](#)

## General Install Procedure  

### Procedure when the machine is introduced to the network

1. Boot machine from network into live system.

2. At command prompt type: paella-submit-machine <name>
   where <name> is the name of the machine.
   
3. Next, type: paella-set-install.  This will instruct 
   the server to create pxe config files for the system
   uuid of the machine.

4. The attributes in the database for the machine will direct the
   pxe config that will be generated.  The type of os, architecture,
   and release are all considered when making the pxeconfig file.
   
### Procedure when machine set to be installed:
 
1. Boot machine from network.  The pxe menu will have an install
   entry at the top that provides the installer with a preseed file 
   generated for the machine.  The user must press enter to boot debian 
   pxe image.
 
2. The machine will then boot the standard debian installer and install 
   a basic system.  The preseed file should provide a way through the 
   early command to send a recipe file to the installer system.  At the 
   moment, the only filesystem being used is the atomic/lvm as provided 
   in the standard debian example preseed file.
 
3. The debian installer will also install salt-minion.  

4. The late command will retrieve a script from the server and 
   execute it.  This script is responsible for identifying the 
   machine for the salt master.  The script will be rendered from 
   a mako template server side with the information that identifies 
   the machine.  The actual identifier of the machine is the URL 
   from where the script is retrieved.
   
5. The script will also send a POST request to the server instructing it 
   that the debian install procedure is about to complete.  The server will 
   then remove the special pxe config file.

6. Once the late command finishes, the debian installer tidies up and 
   unmounts the filesystems, then reboots.  If the machine doesn't default 
   to booting from the network and will boot from the hard drive, the 
   second stage of the installation will continue.  If the machine boots 
   from the network, the default menu option is to boot from the hard 
   drive.
   
 
