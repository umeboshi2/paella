#!/usr/bin/python
import os, sys
import cgi
from xml.dom.minidom import Element, Document
from paella.profile.base import PaellaConnection
from paella.profile.profile import PaellaProfiles


print 'content-type: text/xml'
print

conn = PaellaConnection()
form = cgi.FieldStorage()
profile = 'bard'
if form.has_key('profile'):
    profile = form.getfirst('profile')
p = PaellaProfiles(conn)
d = Document()
ss = d.createProcessingInstruction('xml-stylesheet', 'href="/profile.xsl" type="text/xsl"')
d.appendChild(ss)
d.appendChild(p.export_profile(profile))
d.writexml(sys.stdout, indent='\t', newl='\n', addindent='\t')