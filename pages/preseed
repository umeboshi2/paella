# [Paella](#)

### Preseed builder

The preseed is currently a mako template.  

The preseed file has certain responsibilities beyond automating the first 
stage of the installation.

1. The early command must download and execute a  script that:

	1. Determines the partman recipe for the machine and installs it 
	to the installer filesystem (/tmp/disk-recipe).
	
	2. Overrides the archive.gpg in the installer environment with the 
	key from the local repository.  (This is still problematic and the 
	first stage install is still unauthenticated.)
	
2. The preseed file must install salt-minion.

3. The late command must download and execute a script that:

	1. Configures salt-minion with the identity of the machine.
	
	2. Send a post request to the server informing it that stage one is almost
	complete.  This will cause the server to delete the pxe config files 
	(or alternatively, reconfigure the files to default to hard drive booting).

	3. Preseeds the salt-minion with the installer keys. (This isn't implemented
	yet.  The master is running in open mode.)  The request made above should 
	signal the server to locate the minion keys for the machine, and if no 
	keys are found, to generate them.  The paella server should keep track of 
	all the keys and only set the master to accept those that it preseeds.
	

