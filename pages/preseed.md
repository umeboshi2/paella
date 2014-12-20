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
	  other than modifying the initrd. **IMPORTANT**
	  
2. The preseed file selects the network install interface.  This defaults to 
   eth0, but can be set in the database for machines with multiple interfaces.
   **FIXME**  The netcfg select is currently done on kernel command line, while
   the netcfg question in the preseed defaults to auto.

3. The preseed file must add the salt and paella package repositories to
   the apt sources, and make sure salt-minion is in the list of installed packages.

4. The preseed file must handle the disk in the manner provided by the 
   recipe that is attached to the machine.  This is done by using placing the
   recipe directly in the preseed file.
   
5. The late command must download and execute a script that:

	- Configures salt-minion with the identity of the machine.
	
	- Send a post request to the server informing it that stage one is almost
	  complete.  This will cause the server to delete the pxe config 
	  files.  The default pxe config is configured to boot from the first 
	  hard disk in ten seconds if a key isn't pressed, which helps in the 
	  case that the computer always boots from the network first.

	- **OLD** Preseeds the salt-minion with the installer keys. (This isn't implemented
	  yet.  The master is running in open mode.)  The request made above should 
	  signal the server to locate the minion keys for the machine, and if no 
	  keys are found, to generate them.  The paella server should keep track of 
	  all the keys and only set the master to accept those that it preseeds.

	- **NEW** Preseeds the salt-minion with the installer keys.  The keys are present
	  as python variables in the script.  The script should be conveyed via ssl.  The 
	  keys should already be generated upon the initial submission of the machine.

