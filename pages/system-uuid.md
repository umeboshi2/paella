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


## Rules Concerning System UUID

These are the rules that are intended to be implemented in the paella 
system.

### Submit Machine

Submit machine will submit uuid and name.  UUID is gathered from system 
automatically; name must be entered as command line argument.  This will 
be a POST request. (/paella/api0/machines)

If the uuid is present in the database, the POST request will fail if 
the name is not identical, but will succeed if the name is identical.  The 
name of the machine can be changed on a PUT/PATCH request with 
action='update', as long as the new name doesn't already exist.

### Set Install

The set install script is requesting the machine by uuid using a GET 
request.

If the uuid is present in the database, the server will create the
pxe config files.  The preseed file will need to be retrieved using 
the uuid, rather than the name.  This needs to be true for the late 
command script as well.

### Salt Minion

The salt minion id will be the name of the machine, which will be 
unique.  It seems to be too cumbersome to use the uuid as the minion 
id when maintaining configurations.

## Network Discovery of UUIDs

Using system uuids as identifiers provides a small obstacle to 
having everything that is needed to configure a certain machine 
available to another machine on the network.  It's not intended 
to be a security measure, as it stands, but help a more concerned 
administrator to be able to constrain things more by enabling 
authentication on the paella web server, and using ssl where 
possible.  It may be possible to use http://user:pass@ip/preseed/uuid 






