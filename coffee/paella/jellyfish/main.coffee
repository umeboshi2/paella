#
# Simple RSS app
define (require, exports, module) ->
  Backbone = require 'backbone'
  MSGBUS = require 'msgbus'

  Controller = require 'jellyfish/controller'
  

  class Router extends Backbone.Marionette.AppRouter
    appRoutes:
      'jellyfish': 'start'
      'jellyfish/showpage/:id': 'show_page'
      'jellyfish/editpage/:id': 'edit_page'
      
      
      
  MSGBUS.commands.setHandler 'jellyfish:route', () ->
    console.log "jellyfish:route being handled"
    controller = new Controller
    router = new Router
      controller: controller
    #MSGBUS.commands.setHandler 'sdfsdfrssfeed:create', (model) ->
    #  console.log "rssfeed:create being handled"
    #MSGBUS.commands.setHandler 'sdfsdfrssfeed:update', (model) ->
    #  console.log 'rssfeed:update being handled'
      
      
          