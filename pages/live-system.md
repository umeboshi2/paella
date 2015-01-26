# Default Live System

Boot a machine over the network.  The default boot menu will allow you to 
boot into a live system where you can identify the machine and set a flag 
on the server to install the machine.

Two scripts on the live system:

1. paella-submit-machine <name>
   
   1. sends a name to the server
   
   2. FIXME: the salt config should already have this name
   
   3. the system-uuid is sent to the server
   

2. install-machine
   
   1. machine must already be submitted by script above
   
   2. system uuid is retrieved from the machine
   
   4. the retrieved machine uuid is sent 
   in a POST request dict(action='install', uuid=uuid) to
   http;//host/paella/rest/v0/main/machines .
   
   5. The request above tells the server to create special pxe config 
   files named after the system uuid of the machine.
   
   6. The distinctive feature of the specific pxe config file for the
   system uuid of the target machine is that appends a preseed 
   url to the kernel command line specific to the machine.
   
	   - http://host/paella/preseed/{uuid}
	   
   7. It is the preseed file's duty to make sure salt-minion is installed,
   and the machine identified for the minion to work.  This is currently being 
   done using hostname.

