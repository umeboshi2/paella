# [Paella](#)

### Preseed builder

The preseed is currently a [Mako](http://www.makotemplates.org/) template 
that is served from the paella [server](#pages/paella-server). 

The preseed file has certain responsibilities beyond automating the first 
stage of the installation.

1. The early command must download and execute a  script that:

	- Has the ability to run in the minimal busybox environment.
	
	- Overrides the archive.gpg in the installer environment with the 
	  key from the local repository. This is necessary because the 
	  initrd contains the archive key and there is no other manner of
	  being able to retrieve the udeb packages from the local repository 
	  other than modifying the initrd.
	  
	- (Possibly) Determines the partman recipe for the machine and installs it 
	  to the installer filesystem (/tmp/disk-recipe). This is not 
	  implemented yet.  The recipe could also be included directly 
	  in the preseed since it's coming from the server anyway.
	
2. The preseed file must install salt-minion.

3. The preseed file must handle the disk in the manner provided by the 
   recipe that is attached to the machine.  This could be done by downloading 
   a file into the installer environment, or it could be done by using 
   the preseed template to directly insert the recipe.
   
4. The late command must download and execute a script that:

	- Configures salt-minion with the identity of the machine.
	
	- Send a post request to the server informing it that stage one is almost
	  complete.  This will cause the server to delete the pxe config 
	  files.  The default pxe config is configured to boot from the first 
	  hard disk in ten seconds if a key isn't pressed, which helps in the 
	  case that the computer always boots from the network first.

	- Preseeds the salt-minion with the installer keys. (This isn't implemented
	  yet.  The master is running in open mode.)  The request made above should 
	  signal the server to locate the minion keys for the machine, and if no 
	  keys are found, to generate them.  The paella server should keep track of 
	  all the keys and only set the master to accept those that it preseeds.
	

