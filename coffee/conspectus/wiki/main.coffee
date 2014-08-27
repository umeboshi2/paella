#
# Simple entry app
define (require, exports, module) ->
  Backbone = require 'backbone'
  MSGBUS = require 'msgbus'

  Controller = require 'wiki/controller'

  class Router extends Backbone.Marionette.AppRouter
    appRoutes:
      'wiki': 'start'
      'wiki/listpages': 'list_pages'
      'wiki/showpage/:name' : 'show_page'
      'wiki/editpage/:name': 'edit_page'
      'wiki/addpage': 'add_page'
      
  MSGBUS.commands.setHandler 'wiki:route', () ->
    console.log "wiki:route being handled"
    page_collection = MSGBUS.reqres.request 'pages:collection'
    response = page_collection.fetch()
    response.done =>
      controller = new Controller
      router = new Router
        controller: controller
      console.log 'router created'
