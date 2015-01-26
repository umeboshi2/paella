#
# Simple entry app
define (require, exports, module) ->
  Backbone = require 'backbone'
  MainBus = require 'msgbus'
  AppBus = require 'frontdoor/msgbus'
  
  Controller = require 'frontdoor/controller'
  Util = require 'common/util'
  
  { BootStrapAppRouter } = require 'common/approuters'

  class Router extends BootStrapAppRouter
    appRoutes:
      '': 'start'
      'frontdoor': 'start'
      'pages/:name' : 'show_page'
      
  MainBus.commands.setHandler 'frontdoor:route', () ->
    console.log "frontdoor:route being handled"
    pages = MainBus.reqres.request 'pages:collection'
    response = pages.fetch()
    response.done =>
      controller = new Controller MainBus
      router = new Router
        controller: controller
      controller.show_page 'intro'
