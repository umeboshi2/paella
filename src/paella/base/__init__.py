import os
import logging
from logging.handlers import SysLogHandler

def _Log(name, path=None, logformat=''):
    log = logging.getLogger(name)
    if path is not None:
	hdlr = logging.FileHandler(path)
    else:
	hdlr = SysLogHandler()
    if not logformat:
        logformat = '%(name)s - %(levelname)s: %(message)s'
    frmt = logging.Formatter(logformat)
    hdlr.setFormatter(frmt)
    log.addHandler(hdlr)
    log.setLevel(logging.DEBUG)
    return log

def Log(name, path, format=''):
    return _Log(name, path, logformat=format)

def SysLog(name):
    return _Log(name)

syslog = SysLog('paella-system')


def debug(*something):
    if os.environ.has_key('DEBUG'):
	syslog.debug(' '.join(map(str, something)))

class Error(Exception):
    pass

class ExistsError(Error):
    pass

class NoExistError(Error):
    pass
class NoFileError(NoExistError):
    pass

class UnbornError(NoExistError):
    pass

class KeyError(ExistsError):
    pass

class TableError(ExistsError):
    pass

