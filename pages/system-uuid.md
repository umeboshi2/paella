# [Paella](#)

### System UUID

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

