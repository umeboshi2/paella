#
# Simple entry app
define (require, exports, module) ->
  Backbone = require 'backbone'
  MainBus = require 'msgbus'
  AppBus = require 'frontdoor/msgbus'
  
  Controller = require 'frontdoor/controller'

  { BootStrapAppRouter } = require 'common/approuters'

  class Router extends BootStrapAppRouter
    appRoutes:
      '': 'start'
      'frontdoor': 'start'
      
  MainBus.commands.setHandler 'frontdoor:route', () ->
    console.log "frontdoor:route being handled"
    controller = new Controller MainBus
    router = new Router
      controller: controller
    #console.log 'router created'
