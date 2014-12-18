#
# Simple entry app
define (require, exports, module) ->
  Backbone = require 'backbone'
  MainBus = require 'msgbus'
  WikiBus = require 'wiki/msgbus'
  AppBus = require 'machines/msgbus'
  
  Controller = require 'machines/controller'

  require 'machines/collections'
  
  { BootStrapAppRouter } = require 'common/approuters'

  class Router extends BootStrapAppRouter
    appRoutes:
      '': 'start'
      'machines': 'start'
      'machines/viewrecipe/:name': 'edit_recipe'
      'machines/newrecipe': 'new_recipe'
      'machines/listraid': 'list_raid_recipes'
      'machines/newraid': 'new_raid_recipe'
      
      
  MainBus.commands.setHandler 'machines:route', () ->
    console.log "machines:route being handled"
    recipe_collection = AppBus.reqres.request 'recipe:collection'
    response = recipe_collection.fetch()
    response.done =>
      controller = new Controller MainBus
      router = new Router
        controller: controller
      #console.log 'router created'
