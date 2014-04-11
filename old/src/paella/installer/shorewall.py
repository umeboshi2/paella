import os

RULEACTIONS = ['ACCEPT', 'REDIRECT', 'DNAT', 'DROP', 'REJECT' 'DNAT-', 'CONTINUE', 'LOG']
def maclist_line(iface, hwaddr, ips):
    return '%s\t%s\t%s' % (iface, hwaddr, ','.join(ips))

def redirect_squid(loc, loc_cidr):
    return 'REDIRECT\t%s\t3128\ttcp\twww\t-\t!%s' % (loc, loc_cidr)

class Rule(object):
    def __init__(self, action='ACCEPT', source='net', dest='$FW', dports=None):
        object.__init__(self)
        self.action = action
        self.source = source
        self.dest = dest
        self.proto = 'tcp'
        self.dports = dports
        if self.dports is None:
            self.dports = []
        

    def add_dport(self, dport):
        if dport not in self.dports:
            self.dports.append(dport)

    def __repr__(self):
        parts = [self.action, self.source, self.dest, self.proto, ','.join(self.dports)]
        line = '\t'.join(parts)
        return line

class ForwardRule(Rule):
    def __init__(self, loc, net, dest, dports=None):
        if type(dports) == str:
            dports = [dports]
        dest = '%s:%s' % (loc, dest)
        Rule.__init__(self, action='DNAT', source=net, dest=dest, dports=dports)

    def __repr__(self):
        parts = [self.action, self.source, self.dest, self.proto, ','.join(self.dports), '-', 'all']
        line = '\t'.join(parts)
        return line

class BaseRules(list):
    def __init__(self, loc='loc', net='net'):
        list.__init__(self)
        self.loc = loc
        self.net = net
        self.loc_fw = Rule('ACCEPT', self.loc, '$FW', ['ssh'])
        self.net_fw = Rule('ACCEPT', self.net, '$FW', ['ssh', 'auth'])
        self.append(self.loc_fw)
        self.append(self.net_fw)
        

class FirewalluseRules(object):
    def __init__(self, loc='loc', net='net'):
        object.__init__(self)
        self.loc = loc
        self.net = net
        self.rules = dict.fromkeys(['loc_udp', 'loc_tcp', 'net_udp', 'net_tcp'])


    def _check_rule(self, dest, type):
        key = '%s_%s' % (dest, type)
        print 'key', key
        if dest == 'loc':
            dest = self.loc
        elif dest == 'net':
            dest = self.net
        else:
            raise Exception, 'bad bad bad %s' % dest
        if self.rules[key] is None:
            self.rules[key] = Rule('ACCEPT', '$FW', dest)
            if type != 'tcp':
                self.rules[key].proto = type
                
    def use_smtp(self):
        self._check_rule('net', 'tcp')
        self.rules['net_tcp'].add_dport('smtp')

    def use_domain(self):
        self._check_rule('net', 'tcp')
        self._check_rule('net', 'udp')
        self.rules['net_tcp'].add_dport('domain')
        self.rules['net_udp'].add_dport('domain')

    def use_ntp(self):
        self._check_rule('net', 'udp')
        self.rules['net_udp'].add_dport('ntp')

    def use_www_net(self):
        self._check_rule('net', 'tcp')
        self.rules['net_tcp'].add_dport('www')

    def use_www_loc(self):
        self._check_rule('loc', 'tcp')
        self.rules['loc_tcp'].add_dport('www')

    def get_rules(self):
        return [self.rules[x] for x in self.rules.keys() if self.rules[x] is not None]

    def get_ruleslines(self):
        return [str(rule) + '\n' for rule in self.get_rules()]

class ForwardRules(list):
    def __init__(self, loc='loc', net='net'):
        list.__init__(self)
        self.loc = loc
        self.net = net
        

    def add_rule(self, dest_ip, dport, proto='tcp'):
        rule = ForwardRule(self.loc, self.net, dest_ip, dport)
        self.append(rule)
        
class Shorewall(object):
    def __init__(self, loc='loc', net='net'):
        object.__init__(self)
        self.loc = loc
        self.net = net
        self.base_rules = BaseRules(loc=self.loc, net=self.net)
        self.use_rules = FirewalluseRules(loc=self.loc, net=self.net)
        self.forward_rules = ForwardRules(loc=self.loc, net=self.net)
        self.other_rules = []

    def set_target(self, target):
        self.target = target

    def get_rules(self):
        rules = self.base_rules + self.use_rules.get_rules()
        rules += self.forward_rules + self.other_rules 
        return rules

    def _preplines(self, lines):
        return [str(line) + '\n' for line in lines]
    
    def get_ruleslines(self):
        lines  = self._preplines(self.base_rules) + self.use_rules.get_ruleslines()
        lines += self._preplines(self.forward_rules) + self._preplines(self.other_rules)
        return lines
    
    def get_rulesfile(self):
        lines = file(os.path.join(self.target, 'etc/shorewall/rules')).readlines()
        self.ruleslines = [line for line in lines if line[0] == '#']
        
    def write_rules(self):
        rulesfile = file(os.path.join(self.target, 'etc/shorewall/rules'), 'w')
        top, bottom = self.ruleslines[:-1], self.ruleslines[-1:]
        ruleslines = top + self.get_ruleslines() + bottom
        rulesfile.write(''.join(ruleslines))
        rulesfile.close()

    def redirect_squid(self, loc_cidr):
        self.other_rules.append(redirect_squid(self.loc, loc_cidr))
        
if __name__ == '__main__':
    r = Rule()
    br = BaseRules()
    br.append(redirect_squid('loc', '192.168.0.0/16'))
    f = FirewalluseRules()
    s = Shorewall()
    s.set_target('/mirrors/bkups/tmp')
    s.get_rulesfile()
    s.forward_rules.add_rule('10.0.0.2', 'www')
    s.redirect_squid('10.0.0.0/23')
    
