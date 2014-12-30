# [Paella](#)

## System UUID

The machines on the paella network are identified by their system 
uuid.  In normal network operations, AFAICT, the system uuid is only 
transferred over the network during the PXE negotiation, in plaintext.  
When using paella, the uuid, is transferred over the network in http 
requests by the client when identifying itself to the server.  The paella 
database should not provide a uuid to a paella client.

Even though paella is really meant to be used on a local network where 
the administrator has enough physical access and monitoring ability to 
provide trust during a network install, it would be valuable to raise 
the bar of an attacker to the point of having to discover or guess a 
system uuid.  Due to the nature of PXE, attempts to write code that 
would block an attacker that sniffs the network would be pointless.  
The design is mostly to keep a user of one machine to be able to 
retrieve the pillar data or minion keys of another machine.


## How System UUID is used

These are the rules that are intended to be implemented in the paella 
system.  These are the rules for the unauthenticated access that the 
installer requires to operate.  

The command line tools to submit machines and set them to install 
currently operate in an unauthenticated manner, but this will 
change to require authentication as paella is further developed.


### Major Guidelines

The uuid is the primary identifier for a machine.  The uuid is the 
main token for unauthenticated access.

Machine information cannot be retrieved from a query by the 
name of the machine, nor any other identifier other than the 
uuid of that machine.

The only uuid ever retrieved from the server should match the uuid 
sent in requests by the client.  Normally this will be the machine 
that is being used.  In no circumstance must there be a uuid for 
another machine revealed.  There must be no way to retrieve a map of 
machine names and uuids.


### Submit Machine

Submit machine will submit uuid and name.  UUID is gathered from system 
automatically; name must be entered as command line argument.  This will 
be a POST request. (/paella/api0/machines)

If either the name or the uuid is present in the database, the POST 
request will fail.


### Set Install

The set install script is requesting the machine by uuid using a GET 
request.

If the uuid is present in the database, the server will create the
pxe config files.  The preseed file will need to be retrieved using 
the uuid, rather than the name.  This needs to be true for the late 
command script as well.

### Retrieve machine data

The GET request for a machine's data needs a url with the uuid 
included.  A machine's data cannot be retrieved by the name of 
the machine.


### Preseed and late command files

Preseed files on the server are referred to by uuid.  The url for 
the late command script is also retrieved by uuid.

### Salt Minion

The salt minion id will be the name of the machine, which will be 
unique.  It seems to be too cumbersome to use the uuid as the minion 
id when maintaining configurations.  The actual "minion", or system,
should not be identified by a hardware uuid, yet merely attached to a
single system-uuid that can change when the hardware dies and needs
replacement.



## Network Discovery of UUIDs

Using system uuids as identifiers provides a small obstacle to 
having everything that is needed to configure a certain machine 
available to another machine on the network.  It's not intended 
to be a security measure, as it stands, but help a more concerned 
administrator to be able to constrain things more by enabling 
authentication on the paella web server, and using ssl where 
possible.  It may be possible to use http://user:pass@ip/preseed/uuid 






