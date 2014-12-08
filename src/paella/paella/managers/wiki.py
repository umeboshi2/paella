import os
from datetime import datetime, timedelta
from zipfile import ZipFile
from StringIO import StringIO
import csv
from io import BytesIO

import transaction
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import desc
from sqlalchemy import func

from paella.models.sitecontent import SiteText


class BaseWikiManager(object):
    def __init__(self, session):
        self.session = session

    def query(self):
        return self.session.query(SiteText).filter_by(type='tutwiki')

    def get(self, id):
        return self.session.query(SiteText).get(id)

    def getbyname(self, name):
        q = self.query()
        q = q.filter_by(name=name)
        try:
            return q.one()
        except NoResultFound:
            return None
    

class WikiArchiver(BaseWikiManager):
    def _serialize_page(self, page):
        pdict = dict(id=page.id, name=page.name, type=page.type,
                     created=page.created, modified=page.modified)
        return pdict
    
    def create_new_zipfile(self):
        fields = ['id', 'name', 'type', 'created', 'modified']
        self.zipfileobj = BytesIO()
        self.csvfileobj = StringIO()
        self.zipfile = ZipFile(self.zipfileobj, 'w')
        self.csvfile = csv.DictWriter(self.csvfileobj, fields)
        
    def archive_pages(self):
        for page in self.query().all():
            pdict = self._serialize_page(page)
            self.csvfile.writerow(pdict)
            filename = 'tutwiki-page-%04d.txt' % page.id
            self.zipfile.writestr(filename, bytes(page.content))
        csvfilename = 'tutwiki-dbinfo.csv'
        self.zipfile.writestr(csvfilename, self.csvfileobj.getvalue())
        self.zipfile.close()
        #self.zipfileobj.seek(0)
        #return self.zipfileobj.read()
        return self.zipfileobj.getvalue()
    
            
    

class WikiManager(BaseWikiManager):
    def __init__(self, session):
        super(WikiManager, self).__init__(session)
        self.archiver = WikiArchiver(self.session)
        
    
    def add_page(self, name, content):
        now = datetime.now()
        page = SiteText(name, content, type='tutwiki')
        page.created = now
        page.modified = now
        with transaction.manager:
            self.session.add(page)
        return self.session.merge(page)
    
    def update_page(self, id, content):
        with transaction.manager:
            now = datetime.now()
            page = self.get(id)
            page.content = content
            page.modified = now
            self.session.add(page)
        return self.session.merge(page)

    def list_pages(self):
        return self.query().all()

    def get_page_archive(self):
        self.archiver.create_new_zipfile()
        return self.archiver.archive_pages()
    
