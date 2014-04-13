#!/usr/bin/env python

from pyramid.paster import get_app, setup_logging
ini_path = '/srv/src/paella/development.ini'
setup_logging(ini_path)
application = get_app(ini_path, 'main')


