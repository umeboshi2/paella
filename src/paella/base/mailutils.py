import os, sys
from mailbox import UnixMailbox
from smtplib import SMTP
from email import message_from_file, message_from_string
from email.Message import Message
from email.Generator import Generator
from email.Errors import MessageParseError

def convert_rfc822(fileobj):
    try:
        return message_from_file(fileobj)
    except MessageParseError:
        print 'MessageParseError'
        return ''

class Mailbox(UnixMailbox):
    def __init__(self, fileobj):
        UnixMailbox.__init__(self, fileobj, convert_rfc822)

class GenericMailbox(UnixMailbox):
    def __init__(self, fileobj, fromfield):
        self.__myfromfield__ = fromfield
        _fromlinepattern = r"%s: .*\n" %fromfield
        UnixMailbox.__init__(self, fileobj, convert_rfc822)

    def _search_start(self):
        field = self.__myfromfield__
        lenfield = len(field)
        while 1:
            pos = self.fp.tell()
            line = self.fp.readline()
            if not line:
                raise EOFError
            if line[:lenfield + 2] == field + ': ' and self._isrealfromline(line):
                self.fp.seek(pos)
                return

    def _search_end(self):
        field = self.__myfromfield__
        lenfield = len(field)
        self.fp.readline()      # Throw away header line
        while 1:
            pos = self.fp.tell()
            line = self.fp.readline()
            if not line:
                return
            if line[:lenfield + 2] == field + ': ' and self._isrealfromline(line):
                self.fp.seek(pos)
                return
        
def procmail(infile):
    message = message_from_file(infile)
    


if __name__ == '__main__':
    pass


