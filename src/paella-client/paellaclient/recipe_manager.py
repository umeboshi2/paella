import os
import sys
import subprocess
import json
from optparse import OptionParser
import tempfile

import requests

from paellaclient.base import get_system_uuid
from paellaclient.config import config


base_url = config.get('main', 'recipes_url')
headers = {'Content-type': 'application/json', 'Accept': 'application/json'}

if 'EDITOR' in os.environ:
    editor = os.environ['EDITOR']
else:
    editor = '/usr/bin/editor'
    
REQUIRED_ARG_COMMANDS = ['create', 'edit', 'delete']
COMMANDS = REQUIRED_ARG_COMMANDS + ['list', 'backup', 'restore']

parser = OptionParser()

opts, args = parser.parse_args(sys.argv[1:])

if not len(args):
    raise RuntimeError, "Improper arguments.  Need at least one argument."

command = args[0]
if command not in COMMANDS:
    raise RuntimeError, "Improper command: %s" % command

name = None
if command in REQUIRED_ARG_COMMANDS:
    name = args[1]
    


def get_recipe(name):
    url = os.path.join(base_url, name)
    r = requests.get(url, headers=headers)
    if not r.ok:
        raise RuntimeError, "Something Bad Happened %s" % r
    return json.loads(r.content)

    

def create_recipe(name, content):
    data = dict(name=name, content=content)
    r = requests.post(base_url, data=json.dumps(data), headers=headers)
    if not r.ok:
        raise RuntimeError, "Something Bad Happened %s" % r
    return json.loads(r.content)


def update_recipe(name, content):
    url = os.path.join(base_url, name)
    data = dict(name=name, content=content)
    r = requests.post(url, data=json.dumps(data), headers=headers)
    if not r.ok:
        raise RuntimeError, "Something Bad Happened %s" % r
    return json.loads(r.content)


def delete_recipe(name):
    url = os.path.join(base_url, name)
    r = requests.delete(url, headers=headers)
    if not r.ok:
        raise RuntimeError, "Something Bad Happened %s" % r

def list_recipes():
    url = base_url
    r = requests.get(url, headers=headers)
    if not r.ok:
        raise RuntimeError, "Something Bad Happened %s" % r
    content = json.loads(r.content)
    return content['data']

def edit_content(name, content):
    prefix = 'paella-recipe-%s-' % name
    fd, filename = tempfile.mkstemp(prefix=prefix)
    with os.fdopen(fd, 'w') as recipe_file:
        recipe_file.write(content)
    #proc = subprocess.Popen([editor, filename])
    subprocess.check_call([editor, filename])
    with file(filename) as recipe_file:
        new_content = recipe_file.read()
    os.remove(filename)
    if os.path.isfile(filename):
        raise RuntimeError, "%s still exists." % filename
    return new_content

def edit_recipe(name):
    recipe = get_recipe(name)
    content = edit_content(name, recipe['content'])
    if content != recipe['content']:
        update_recipe(name, content)
        



def main():
    if command == 'create':
        if name in list_recipes():
            raise RuntimeError, "A recipe named %s already exists." % name
        create_recipe(name, '')
        edit_recipe(name)
        print "Recipe %s created." % name
    if command == 'edit':
        if name not in list_recipes():
            raise RuntimeError, "No recipe named %s exists." % name
        edit_recipe(name)
        print "Recipe %s updated." % name

    if command == 'delete':
        if name not in list_recipes():
            raise RuntimeError, "No recipe named %s exists." % name
        delete_recipe(name)
        print "Recipe %s deleted." % name

    if command == 'list':
        for r in list_recipes():
            print r
            
    if command == 'backup':
        for r in list_recipes():
            filename = '%s.recipe' % r
            content = get_recipe(r)['content']
            with file(filename, 'w') as outfile:
                outfile.write(content)

    if command == 'restore':
        suffix = '.recipe'
        recipe_files = [f for f in os.listdir('.') if f.endswith(suffix)]
        for filename in recipe_files:
            name = filename[:-len(suffix)]
            with file(filename) as infile:
                content = infile.read()
            create_recipe(name, content)
            
    
if __name__ == '__main__':
    main()
    
        
