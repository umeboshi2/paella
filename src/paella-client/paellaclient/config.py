from ConfigParser import ConfigParser
from StringIO import StringIO


DEFAULT_CONFIG_TEXT = """\
# Configuration file for paella-client

[main]
# FIXME don't use ip address here
machines_url: http://paella/paella/rest/v0/main/machines
recipes_url: http://paella/paella/rest/v0/main/recipes
debrepos_url: http://paella/paella/rest/v0/main/debrepos
"""

config = ConfigParser()
config.readfp(StringIO(DEFAULT_CONFIG_TEXT))
config.read(['/etc/paella.conf'])
