#
# Simple RSS app
define (require, exports, module) ->
  Backbone = require 'backbone'
  MSGBUS = require 'msgbus'

  Controller = require 'simplerss/controller'
  

  class Router extends Backbone.Marionette.AppRouter
    appRoutes:
      'simplerss': 'start'
      'simplerss/showfeed/:id': 'show_feed'
      'simplerss/editfeed/:id': 'show_edit_feed_form'
      'simplerss/addfeed': 'show_new_feed_form'
      
      
  MSGBUS.commands.setHandler 'simplerss:route', () ->
    console.log "simplerss:route being handled"
    controller = new Controller
    router = new Router
      controller: controller
    MSGBUS.commands.setHandler 'rssfeed:create', (model) ->
      console.log "rssfeed:create being handled"
      controller.new_feed_added model
    MSGBUS.commands.setHandler 'rssfeed:update', (model) ->
      console.log 'rssfeed:update being handled'
      controller.feed_info_updated model
      
      
          