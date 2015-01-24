# [Paella](#)

## TODO

### General

- **FILE ISSUES ON GITHUB AND GET RID OF THIS TODO**

- need to respect arch decision when installing ostype mswindows

- work on deployment plan

- Start preparing to handle both amd64 and i386. (STARTED)

	- DONE: make sure debian installs work on both archs
	
	- make sure that mswindows ostype installs with live system (STARTED)
	

- Setup scripts to help with partial repository STARTED

- Move more info into pillar data

  - wipe out all hardcoded entries of '10.0.4.1' to config files or pillar data (DONE)

- Handle different operating system releases

	- test using debian jessie pxe boot (DONE)
	
	- windows is left as local exercise due to availability of content
	

- Decide how to handle newer UEFI systems.

- Work on [deployment](#pages/deployment) notes.

- Use debian live system to install custom wim image and prepare boot.

- Virtualbox fails to reboot PXE, needs poweroff.  Determine if this is true
for both wheezy and jessie.  Verify, then reportbug.

- Implement just enough DNS on paella server to add paella CNAME
entry.  Fix paella-client to use paella hostname by default for paella server. (DONE)

- Create default disk recipes and some sitetext pages for the paella server.

- Make fstab entries for loopback mounted iso files.

- Three pillar files hold "paella_server_ip".  Make sure paella-client talks
to paella host instead of ip address.  The .ini file that paella sever uses
also has "paella_server_ip" defined.  In total, there are currently four
files that contain "paella_server_ip."  Consolidate the three pillar files into
a single file, then make notes that there are only two files to adjust when
changing "paella_server_ip" for vagrant machine. (DONE, all variables should be in bvars.jinja(todo: rename))

- Make note that 10.0.2.0/24 cidr interferes with default NAT addresses
on virtualbox.  Make note that option to change this is commented out
in Vagrantfile.

- Consider using vagrant rsync updates for some shared directories. (UNSURE IF NEEDED)



### Paella Server

- Automate key generation and preseed the keys during first stage 
  install.
  http://docs.saltstack.com/en/latest/topics/tutorials/preseed_key.html
  - pyramid_celery and rabbitmq to help queue key generation jobs
  - minion keys are generated and accepted on server on submit machine
  - minion keys remain in database
  - keys are installed to minion in configure netboot script (latecmd)
  - **IMPORTANT** need to enforce ssl on apache to pass data across network

- Implement per machine auto install option when generating install pxe 
config file.  Implement a short delay in pxeconfig, but still automatically install
system.

- work on web interface

	- edit state files with ace editor

	- change layout a bit and put paella management in it's own page.

	- create front page  and cleanup unneeded applets **STARTED**

	- implement specific machine templates.  Create, edit and add/remove
	to/from machine.

	- get wiki/sitetext working properly on web interface.

	- check pxeconfig on machine update, and refresh pxeconfig if exists.

	- create interface to assign release to machine.  Release is just simple
	text field with hardcoded entries.  **FIXME** figure out nice way to
	manage release info.
	

### Debian Installs

- Can we put the debian installer in an LXC container on the debian-live system?

- Create some simple disk/partition recipes to use as a starting 
  point.(STARTED)
  - a couple of recipes have been created.
  - find place in repos to place recipes for db init

- test raid recipes and determine if disklist is needed in database
  - can we presume disklist on null entry in db?

- need place for kernel cmdline parameters in machine row

- think about making a special section in preseed to handle the  disk options.  The
  special section will include debconf questions and answers that complement the
  recipes. It looks like a disk list will be needed to use the raid recipe.  Can I create
  a reasonable disk list by reading the raid recipe on the server and answering the
  disk list question in the template?

### Windows Installs

- Look at using streamable WIM's using wimlib.  Serve WIM based on 
  uuid.  Serve unattend.xml based on uuid.
  
- Make image capture and submission scripts. Should WIM's get their 
  own database table?

- Make sample autounattend.xml for 64 bit windows.

- handle windows releases other than 7, and also possibly support flavors.

- integrate preexisting windows into paella server on deployment to client network.
  **IMPORTANT**, I forgot what I meant by this statement.

- look at using wimboot instead of booting winpe iso's.

### Completed!

- DONE: Make scripts for live netboot system to identify machines and set
  for install.
  
- DONE: Make server that accepts POST requests and assigns machine names 
  to mac addresses.
  
- DONE: Get server to render preseed files based on name of machine.

- DONE: Get server to create and destroy pxe config files for machines in 
  /var/lib/tftpboot.

- DONE: use system uuid instead of mac addresses: dmidecode -s system-uuid

- DONE: web-interface:  recipe managers


