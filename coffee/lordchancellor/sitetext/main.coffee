define (require, exports, module) ->
  Backbone = require 'backbone'
  MainBus = require 'msgbus'

  Controller = require 'sitetext/controller'
  AppBus = require 'sitetext/msgbus'

  { BootStrapAppRouter } = require 'common/approuters'
    
  # require this for msgbus handlers
  require 'useradmin/collections'
  
  class Router extends BootStrapAppRouter
    appRoutes:
      'sitetext': 'start'
      'sitetext/listpages': 'list_pages'
      'sitetext/addpage': 'add_page'
      'sitetext/editpage/:name': 'edit_page'
      'sitetext/showpage/:name': 'show_page'

  MainBus.commands.setHandler 'sitetext:route', () ->
    console.log 'sitetext:route being handled'
    controller = new Controller
    router = new Router
      controller: controller
