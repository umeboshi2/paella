#!/usr/bin/env python
import os, sys
import json

pages_dir = 'pages'

if not os.path.isdir(pages_dir):
    raise RuntimeError, "Pages directory doesn't exist."

base_dir = os.getcwd()

os.chdir(pages_dir)

md_suffix = '.md'

files = [f for f in os.listdir('.') if f.endswith(md_suffix)]
pages = list()
for filename in files:
    name = filename[:-len(md_suffix)]
    title = file(filename).next().strip()
    #pages[name] = title
    page = dict()
    page['id'] = name
    page['title'] = title
    data = dict(id=name, content=file(filename).read())
    json_filename = '%s.json' % name
    with file(json_filename, 'w') as outfile:
        json.dump(data, outfile)
    print "created", json_filename
    pages.append(page)
    
index_filename = 'index.json'
#data = dict(pages=pages)
data = pages
with file(index_filename, 'w') as outfile:
    json.dump(data, outfile)
    print "created", index_filename
