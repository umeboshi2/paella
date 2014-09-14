define (require, exports, module) ->
  Backbone = require 'backbone'
  MainBus = require 'msgbus'

  Controller = require 'wiki/controller'
  AppBus = require 'wiki/msgbus'

  { BootStrapAppRouter } = require 'common/approuters'
    
  # require this for msgbus handlers
  require 'wiki/collections'
  
  class Router extends BootStrapAppRouter
    appRoutes:
      'wiki': 'start'
      'wiki/listpages': 'list_pages'
      'wiki/showpage/:name' : 'show_page'
      'wiki/editpage/:name': 'edit_page'
      'wiki/addpage': 'add_page'
      
  MainBus.commands.setHandler 'wiki:route', () ->
    console.log "wiki:route being handled"
    page_collection = AppBus.reqres.request 'pages:collection'
    response = page_collection.fetch()
    response.done =>
      controller = new Controller MainBus
      router = new Router
        controller: controller
      #console.log 'router created'
