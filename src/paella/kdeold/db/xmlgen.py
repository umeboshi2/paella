#from operator import and_
from xml.dom.minidom import Element, Text

from paella.base import NoExistError
from paella.sqlgen.clause import Eq, In

from kommon.base.xmlgen import Html, Body, Anchor
from kommon.base.xmlgen import BR, HR, Bold
from kommon.base.xmlgen import TR, TD
from kommon.base.xmlgen import TableElement
from kommon.base.xmlgen import BaseElement, TextElement
