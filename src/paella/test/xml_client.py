from xmlrpclib import ServerProxy, SafeTransport

from paella.base import debug, Error
from paella.debian.base import RepositorySource, islocaluri



tc = ServerProxy('http://premio:8000', None, None, 0, allow_none=True)
