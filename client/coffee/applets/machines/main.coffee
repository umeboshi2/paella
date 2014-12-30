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
      'machines': 'start'
      'machines/viewmachine/:name': 'view_machine'

      
  MainBus.commands.setHandler 'machines:route', () ->
    console.log "machines:route being handled"
    controller = new Controller MainBus
    router = new Router
      controller: controller
