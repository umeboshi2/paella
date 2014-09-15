conspectus
==========

A basic skeleton for a project serving static resources

create app to serve static resources for website

only client side code and other static resources

index.html is for static sites, otherwise these are static resources for another service

index.local.html is for pre-optimized code

use python and templates (maybe mako) to make generic skeleton

add fontawesome to index page



depends
-------

python

node

compass

grunt


basic structure
----------------

Common

- util
  - basic utilities used throughout project
- mainpage
  - initialize main page with layout and navbar
- mainviews
  - layout and navbar views for mainpage
- templates
  - templates for layout and navbar views
  - common sidebar template
- approuters
  - special router to set 'active' class on navbar
- basecollection
  - common parse code to bypass sending a bare 
    array object as a json response
- controllers
  - basic controller with attached utils
  - sidebar controller
- localstoragemodel
  - simple model with localStorage backend (not really useful)
- views
  - sidebar
    - basic sidebar view
  - formview
    - simple form view
  - editor
    - base view using ace editor

Site

- main
  - configure requirejs paths
  - start application
- application
  - create appmodel
  - prepare regions and start backbone history
  - init main page
  - init app routers
  - setup event handlers for managing views in app regions
- msgbus
  - MainBus
  - main channel for messages, events, and commands
- models
  - sitewide models
- collections
  - sitewide collections

App

- main
  - setup router and routes
  - attach controller to router
- msgbus
  - AppBus for app messages, events, and commands
- models
  - app models
- collections
  - app collections
- templates
  - templates for the views
- views
  - views for the app
- controller
  - controller for app
  - manage views

#Todo

- fix api for site text
- provide site text for guest
- add groups
- add/remove users to/from groups
- remove localstorage and use memory and defaults in code
- create docs on common modules
- use jquery-cookie to set session cookie from server and
  don't refresh page.
- rearrange manner in which bower components are handled
- test using grunt-bower-requirejs
- create a multipage build config with a common stack
  - consider making separate modules for ace and other large libs that are
	only occasionally used.
	
  
