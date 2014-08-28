#
# Simple entry app
define (require, exports, module) ->
  Backbone = require 'backbone'
  MainBus = require 'msgbus'
  WikiBus = require 'wiki/msgbus'
  AppBus = require 'frontdoor/msgbus'
  
  Controller = require 'frontdoor/controller'

  class Router extends Backbone.Marionette.AppRouter
    appRoutes:
      '': 'start'
      'frontdoor': 'start'
      
  MainBus.commands.setHandler 'frontdoor:route', () ->
    console.log "frontdoor:route being handled"
    page_collection = WikiBus.reqres.request 'pages:collection'
    response = page_collection.fetch()
    response.done =>
      controller = new Controller
      router = new Router
        controller: controller
      console.log 'router created'
