define (require, exports, module) ->
  Backbone = require 'backbone'
  MainBus = require 'msgbus'

  Controller = require 'useradmin/controller'
  AppBus = require 'useradmin/msgbus'

  { BootStrapAppRouter } = require 'common/approuters'
    
  # require this for msgbus handlers
  require 'useradmin/collections'
  
  class Router extends BootStrapAppRouter
    appRoutes:
      'useradmin': 'start'
      'useradmin/listusers': 'list_users'
      'useradmin/adduser': 'add_user'
      'useradmin/listgroups': 'list_groups'
      'useradmin/addgroup': 'add_group'
      'useradmin/viewuser/:id': 'view_user'

  MainBus.commands.setHandler 'useradmin:route', () ->
    console.log 'useradmin:route being handled'
    controller = new Controller MainBus
    router = new Router
      controller: controller
