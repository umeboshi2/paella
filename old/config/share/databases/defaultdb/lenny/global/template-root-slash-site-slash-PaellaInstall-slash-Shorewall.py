# -*- mode: python -*-
import sys

from useless.base.path import path

from paella.installer.toolkit import InstallerTools

def marker(line):
    # the marker is #start foo2bar
    if line.startswith('#start'):
        ruletype = line.split()[1]
        # strip the newline before returning
        # the ruletype
        return ruletype.strip()
    else:
        return None

def parse_ruletype(ruletype):
    src, dest = ruletype.split('2')
    if src == 'fw':
        src = '$FW'
    if dest == 'fw':
        dest = '$FW'
    return src, dest

def make_rule(ruletype, macro, action="ACCEPT"):
    src, dest = parse_ruletype(ruletype)
    line = '%s/%s\t%s\t\t%s\n' % (macro, action, src, dest)
    return line

def make_trait_rule(ruletype, trait, action="ACCEPT"):
    raise RuntimeError , "make_trait_rule should not be called"
    macro = TRAITMACROS[trait]
    return make_rule(ruletype, macro, action=action)


def testget(key):
    if key == 'net2fw':
        return "HTTP HTTPS"
    if key == 'loc2fw':
        return "HTTP HTTPS SMB NTP"
    if key == 'fw2net':
        return "#HTTP #HTTPS NTP"
    if key == 'fw2loc':
        return "SMB NTP"
    raise RuntimeError , 'Unknown key %s' % key

    
def get(key):
    if ':' not in key:
        key = 'firewall:%s' % key
    return env.dereference(key)

class ShorewallRules(object):
    def __init__(self, toolkit):
        self.it = toolkit
        self.RULETYPES = ['fw2net', 'fw2loc', 'net2fw', 'loc2fw']
        self.RULETYPE_MACROS = {}
        for ruletype in self.RULETYPES:
            key = '%s_macros' % ruletype
            macros = self.get(key).split()
            self.RULETYPE_MACROS[ruletype] = macros
        self.rules_filename = self.it.target / 'etc/shorewall/rules'


    def get(self, key):
        if ':' not in key:
            key = 'firewall:%s' % key
        return self.it.get(key)

    def make_rules_lines(self):
        orig_rules_lines = self.rules_filename.lines()
        rules_lines = []
        for line in orig_rules_lines:
            rules_lines.append(line)
            ruletype = marker(line)
            if ruletype is not None:
                macros = self.RULETYPE_MACROS[ruletype]
                for macro in macros:
                    print "adding", ruletype, macro, "to rules"
                    rules_lines.append(make_rule(ruletype, macro))
        return rules_lines

    def write_rules_file(self):
        lines = self.make_rules_lines()
        file(self.rules_filename, 'w').writelines(lines)
        

    
