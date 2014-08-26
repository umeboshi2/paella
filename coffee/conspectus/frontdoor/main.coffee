#
# Simple entry app
define (require, exports, module) ->
  Backbone = require 'backbone'
  MSGBUS = require 'msgbus'

  Controller = require 'frontdoor/controller'

  class Router extends Backbone.Marionette.AppRouter
    appRoutes:
      '': 'start'
      'frontdoor': 'start'
      'pages/:name' : 'show_page'
      
  MSGBUS.commands.setHandler 'frontdoor:route', () ->
    console.log "frontdoor:route being handled"
    controller = new Controller
    router = new Router
      controller: controller
    console.log 'router created'
    