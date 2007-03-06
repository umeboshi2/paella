from useless.base.util import ujoin

from useless.db.midlevel import Environment

class TraitEnvironment(Environment):
    def __init__(self, conn, suite, trait):
        self.suite = suite
        table = ujoin(suite, 'variables')
        Environment.__init__(self, conn, table, 'trait')
        self.set_main(trait)


if __name__ == '__main__':
    #f = file('tmp/trait.xml')
    #tx = TraitXml(f)
    import sys
