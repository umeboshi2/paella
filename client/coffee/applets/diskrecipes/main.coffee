#
# Simple entry app
define (require, exports, module) ->
  Backbone = require 'backbone'
  MainBus = require 'msgbus'
  WikiBus = require 'wiki/msgbus'
  AppBus = require 'diskrecipes/msgbus'
  
  Controller = require 'diskrecipes/controller'

  require 'diskrecipes/collections'
  
  { BootStrapAppRouter } = require 'common/approuters'

  class Router extends BootStrapAppRouter
    appRoutes:
      'diskrecipes': 'start'
      'diskrecipes/viewrecipe/:name': 'edit_recipe'
      'diskrecipes/newrecipe': 'new_recipe'
      'diskrecipes/listraid': 'list_raid_recipes'
      'diskrecipes/newraid': 'new_raid_recipe'
      'diskrecipes/viewraid/:name': 'edit_raid_recipe'
      
  MainBus.commands.setHandler 'diskrecipes:route', () ->
    console.log "diskrecipes:route being handled"
    controller = new Controller MainBus
    router = new Router
      controller: controller
