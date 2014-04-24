from ConfigParser import ConfigParser
from StringIO import StringIO


DEFAULT_CONFIG_TEXT = """\
# Configuration file for paella-client

[main]
# FIXME don't use ip address here
machines_url: http://10.0.4.1/paella/api0/machines
recipes_url: http://10.0.4.1/paella/api0/recipes
"""

config = ConfigParser()
config.readfp(StringIO(DEFAULT_CONFIG_TEXT))
config.read(['/etc/paella.conf'])
