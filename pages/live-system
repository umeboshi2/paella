# [Paella](#)

#### Default Live System

Boot a machine over the network.  The default boot menu will allow you to 
boot into a live system where you can identify the machine and set a flag 
on the server to install the machine.

Two scripts on the live system:

1. paella-submit-machine <name>
   
   1. sends a name to the server
   
	   - actually sends json.dumps(
		 dict(action='submit', machine=name, addresses=[a1, a2]))
		 in a POST request to http://host/paella/machines
   
   2. the salt config should already have this name
   
   3. all mac addresses sent to server and tied to name
   

2. install-machine
   
   1. machine must already be submitted by script above
   
   2. name lookup based on matching mac address
   
   3. the script gets addresses on local machine then checks 
   http://host/paella/addresses/{address} for a machine name, 
   accepting the first match.
		 
   4. after a successful match, the retrieved machine name is sent 
   in a POST request dict(action='install', machine=name) to
   http;//host/paella/machines .
   
   5. The request above tells the server to create special pxe config 
   files named after the mac addresses linked to the machine in the 
   database.
   
   6. The distinctive feature of the specific pxe config file for the
   mac address of the target machine is that appends a preseed 
   url to the kernel command line specific to the machine.
   
	   - http://host/paella/preseed/{machine}
	   
   7. It is the preseed file's duty to make sure salt-minion is installed,
   and the machine identified for the minion to work.  This is currently being 
   done using hostname.

