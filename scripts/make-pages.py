#!/usr/bin/env python
import os, sys
import json

ignored_suffixes = ['.json', '~']

pages_dir = 'pages'

if not os.path.isdir(pages_dir):
    raise RuntimeError, "Pages directory doesn't exist."

base_dir = os.getcwd()

os.chdir(pages_dir)

files = os.listdir('.')
for suffix in ignored_suffixes:
    files = [f for f in files if not f.endswith(suffix)]

for filename in files:
    data = dict(id=filename, content=file(filename).read())
    json_filename = '%s.json' % filename
    with file(json_filename, 'w') as outfile:
        json.dump(data, outfile)
    print "created", filename
    
