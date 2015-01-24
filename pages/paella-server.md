# Paella Server

The paella server is a [Pyramid](http://www.pylonsproject.org/) web 
server that has a simple
[REST](http://en.wikipedia.org/wiki/Representational_state_transfer) 
interface for handling the machines.  The web server is also responsible 
for serving the preseed files and configuration scripts that are 
specific to the machine being installed or configured.  At this time, 
the paella server **must** have write access to the pxelinux.cfg directory 
in the directory that contains the pxelinux.0 file mentioned by the 
dhcp server.  This is currently hardcoded to /var/lib/tftpboot/pxelinux.cfg 
and needs to be adapted.

The paella server will also help with maintaining partial local debian 
repositories.

## Browser Client

The client is being written on the paella branch of [conspectus](https://github.com/umeboshi2/conspectus.git).  Authentication will be required to perform any useful
management action on a machine.


## REST Interface

### Prefix

The current prefix for all requests in /paella/rest/v0/main


### /machines

This is the main url for managing the machines from the target machine.  All
POST and GET requests have an "action" parameter.  Also, all POST and GET
requests require a **uuid** paramater to identify the machine making the
request.

#### GET Actions

- /machines/{uuid}
  This will basically get a JSON machine object from the database.

#### POST Actions

- **submit** (name, uuid)  
  This is the command that creates a machine in the database,
  with a unique name tied to the system uuid.

- **install** (uuid)  
  This is the command that instructs the server to create a
  PXE config file for the machine identified by the uuid.

- **stage_over** (uuid)  
  This is the command that instructs the server to delete the 
  PXE config file for the machine identified by the uuid.

- **update_machine** (name=None, recipe=None, autoinstall=None)
  /admin/machines/{uuid}
  Any parameter that is not None will be updated accordingly in the 
  database.  The autoinstall paramater is boolean. The recipe is 
  identified by a unique name.
  
- **update_package_list**
  This needs to be done with another url.


### /admin/machines


### /recipes and /recipes/{name}

This is a simple CRUD interface for the partman recipes.


## Other endpoints

### /paella/preseed/{uuid}

This url provides the [preseed](#pages/preseed) file for the 
debian installer.

### /paella/latecmd/{uuid}

This url provides the late command for the debian installer.