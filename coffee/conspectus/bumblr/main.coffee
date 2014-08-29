#
define (require, exports, module) ->
  Backbone = require 'backbone'
  Util = require 'common/util'
  MainBus = require 'msgbus'

  Controller = require 'bumblr/controller'
  AppBus = require 'bumblr/msgbus'

  { BootStrapAppRouter } = require 'common/approuters'
  

  # FIXME: this is to make sure that AppBus handlers
  # are running
  Models = require 'bumblr/models'  
  require 'bumblr/collections'
  
  class Router extends BootStrapAppRouter
    appRoutes:
      'bumblr': 'start'
      'bumblr/settings': 'settings_page'
      'bumblr/dashboard': 'show_dashboard'
      'bumblr/listblogs': 'list_blogs'
      'bumblr/viewblog/:id': 'view_blog'
      'bumblr/addblog' : 'add_new_blog'
      
  current_calendar_date = undefined
  AppBus.commands.setHandler 'maincalendar:set_date', () ->
    cal = $ '#maincalendar'
    current_calendar_date = cal.fullCalendar 'getDate'

  AppBus.reqres.setHandler 'maincalendar:get_date', () ->
    current_calendar_date
    
  MainBus.commands.setHandler 'bumblr:route', () ->
    console.log "bumblr:route being handled..."
    blog_collection = AppBus.reqres.request 'get_local_blogs'
    response = blog_collection.fetch()
    response.done =>
      controller = new Controller
      router = new Router
        controller: controller
      #console.log 'bumblr router created'
