#
# Simple RSS app
define (require, exports, module) ->
  Backbone = require 'backbone'
  MSGBUS = require 'msgbus'

  Controller = require 'frontdoor/controller'
  #Collections = require 'collections'
  #Models = require 'models'
  
  
  #feeds = MSGBUS.reqres.request 'rss:feedlist'

  class Router extends Backbone.Marionette.AppRouter
    appRoutes:
      '': 'start'
      'frontdoor': 'start'
      
  MSGBUS.commands.setHandler 'frontdoor:route', () ->
    console.log "frontdoor:route being handled"
    controller = new Controller
    router = new Router
      controller: controller
    