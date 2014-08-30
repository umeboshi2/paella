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

