from xml.dom.minidom import Text

from konsultant.base.xmlgen import BaseElement, TextElement
from konsultant.base.xmlgen import Anchor, Html, Body
from konsultant.base.xmlgen import ListItem, UnorderedList
from konsultant.base.xmlgen import BR, HR, Bold, TR, TD, Paragraph
from konsultant.base.xmlgen import SimpleTitleElement, RecordElement

from paella.profile.trait import Trait

class BaseDocument(BaseElement):
    def __init__(self, app, **atts):
        BaseElement.__init__(self, 'html', **atts)
        self.app = app
        self.conn = app.conn
        self.body = Body()
        self.appendChild(self.body)

    def clear_body(self):
        while self.body.hasChildNodes():
            del self.body.childNodes[0]

class TxtTD(TD):
    def __init__(self, text):
        TD.__init__(self)
        node = Text()
        node.data = text
        self.appendChild(node)
        
class TraitEnvTable(RecordElement):
    def __init__(self, trait, env, **atts):
        fields = env.keys()
        fields.sort()
        RecordElement.__init__(self, fields, 'trait', None, env, **atts)
        
class SectionTitle(SimpleTitleElement):
    def __init__(self, text, **atts):
        atts['width'] = '75%'
        atts['bgcolor'] = 'IndianRed'
        SimpleTitleElement.__init__(self, text, **atts)

class PackageTable(BaseElement):
    def __init__(self, rows, **atts):
        BaseElement.__init__(self, 'table', **atts)
        for row in rows:
            print row
            trow = TR()
            p = TxtTD(row.package)
            trow.appendChild(p)
            a = TxtTD(row.action)
            trow.appendChild(a)
            self.appendChild(trow)

class TemplateTable(BaseElement):
    def __init__(self, rows, **atts):
        BaseElement.__init__(self, 'table', **atts)
        for row in rows:
            print row
            trow = TR()
            fake_template = ',,,'.join([row.package, row.template.replace('.', ',')])
            ta = Anchor('show.template.%s' % fake_template, row.template)
            td = TD()
            td.appendChild(ta)
            trow.appendChild(td)
            p = TxtTD(row.package)
            trow.appendChild(p)
            self.appendChild(trow)
        
        
class TraitDoc(BaseDocument):
    def __init__(self, app, **atts):
        BaseDocument.__init__(self, app, **atts)
        self.trait = Trait(self.conn)

    def set_trait(self, trait):
        self.clear_body()
        self.trait.set_trait(trait)
        title = SimpleTitleElement('Trait: %s' % trait, bgcolor='IndianRed', width='100%')
        self.body.appendChild(title)
        plist = UnorderedList()
        parents = self.trait.parents(trait=trait)
        print self.trait.suite
        print parents, trait
        self.body.appendChild(SectionTitle('Parents'))
        for parent in parents:
            print 'trait parent', trait, parent
            pp = Anchor('show.parent.%s' % parent, parent)
            plist.appendChild(ListItem(pp))
        self.body.appendChild(plist)
        ptitle = Anchor('edit.packages.%s' % trait, 'Packages')
        self.body.appendChild(SectionTitle(ptitle))
        rows = self.trait.packages(trait=trait, action=True)
        self.body.appendChild(PackageTable(rows, bgcolor='SkyBlue3'))
        ttitle = Anchor('edit.templates.%s' % trait, 'Templates')
        self.body.appendChild(SectionTitle(ttitle))
        rows = self.trait.templates(trait=trait, fields=['package', 'template', 'templatefile'])
        if len(rows):
            self.body.appendChild(TemplateTable(rows, bgcolor='DarkSeaGreen3'))
        self.body.appendChild(SectionTitle('Variables', href='foo.var.ick'))
        if len(self.trait.environ.keys()):
            env = TraitEnvTable(trait, self.trait.environ, bgcolor='MistyRose3')
            print 'env', self.trait.environ.keys()
            self.body.appendChild(env)
        self.body.appendChild(SectionTitle('Scripts'))
        slist = UnorderedList()
        for row in self.trait._scripts.scripts(trait=trait):
            script  = row.script
            sa = Anchor('show.script.%s' % script, script)
            slist.appendChild(ListItem(sa))
        self.body.appendChild(slist)
        
