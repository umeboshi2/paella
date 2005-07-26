#!/usr/bin/env python
import os, sys
import cgi
from xml.dom.minidom import Element, Document

from paella.db import PaellaConnection
from paella.db.profile.main import PaellaProfiles


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
