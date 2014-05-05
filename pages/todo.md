# [Paella](#)

## TODO

- Setup scripts to help with partial repository STARTED

- Move more info into pillar data

  - wipe out all hardcoded entries of '10.0.4.1' to config files or pillar data

- Create some simple disk/partition recipes to use as a starting 
  point.
  
- Automate key generation and preseed the keys during first stage 
  install.
  http://docs.saltstack.com/en/latest/topics/tutorials/preseed_key.html

- Implement per machine auto install option when generating install pxe 
  config file.

- Start preparing to handle both amd64 and i386. (STARTED)

	- make sure debian installs work on both archs
	
	- make sure that mswindows ostype installs with live system
	

- Handle different operating system releases

	- test using debian jessie pxe boot
	
	- windows is left as local exercise due to availability of content
	

- Decide how to handle newer UEFI systems.

- DONE: Make scripts for live netboot system to identify machines and set
  for install.
  
- DONE: Make server that accepts POST requests and assigns machine names 
  to mac addresses.
  
- DONE: Get server to render preseed files based on name of machine.

- DONE: Get server to create and destroy pxe config files for machines in 
  /var/lib/tftpboot.

- DONE: use system uuid instead of mac addresses: dmidecode -s system-uuid

- Work on [deployment](#pages/deployment) notes.

- Use debian live system to install custom wim image and prepare boot.

- Look at using streamable WIM's using wimlib.  Serve WIM based on 
  uuid.  Serve unattend.xml based on uuid.
  
- Make image capture and submission scripts. Should WIM's get their 
  own database table?
  

  
