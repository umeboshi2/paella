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
      'wiki/listpages': 'list_pages'
      'wiki/showpage/:name' : 'show_page'
      'wiki/editpage/:name': 'edit_page'
      'wiki/addpage': 'add_page'
      
  MSGBUS.commands.setHandler 'frontdoor:route', () ->
    console.log "frontdoor:route being handled"
    page_collection = MSGBUS.reqres.request 'pages:collection'
    response = page_collection.fetch()
    response.done =>
      controller = new Controller
      router = new Router
        controller: controller
      console.log 'router created'
