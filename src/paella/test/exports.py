
from paella.contrib.pyparsing import Word, alphas, Literal, nums, Suppress
from paella.contrib.pyparsing import restOfLine, Optional, Dict, ZeroOrMore
from paella.contrib.pyparsing import Group, OneOrMore, LineStart, Combine
from paella.contrib.pyparsing import delimitedList, Forward




ipn = Word(nums) ^ Literal('*')

ip = Combine(ipn + '.' + ipn + '.' + ipn + '.' + ipn)
hostname = Word(alphas + nums + '-_*+')
cidr = ip + '/' + Word(nums)
ntbm = ip + '/' + ip

export_options = ['rw', 'ro', 'sync', 'async', 'no_root_squash']


def ExportsParser():
    comment = '#' + Optional(restOfLine)
    exportpath = LineStart() + Word(alphas + nums + '/_-')
    clientname = Word(alphas + nums + '/_-.*')
    clientopts = Suppress('(') + Group(OneOrMore(Word(alphas+'_') + Optional(Suppress(',')))) + Suppress(')')
    client = clientname + clientopts
    clients = Group(OneOrMore(client))
    exportline = exportpath + clients + restOfLine
    exports = Group(exportline)
    exports.ignore(comment)
    return ZeroOrMore(exports)

if __name__ == '__main__':
    ep = ExportsParser()
    d = ep.parseString(file('exports').read())
