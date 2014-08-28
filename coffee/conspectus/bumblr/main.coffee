#
define (require, exports, module) ->
  Backbone = require 'backbone'
  MSGBUS = require 'msgbus'

  Controller = require 'bumblr/controller'

  # FIXME: this is to make sure that MSGBUS handlers
  # are running
  Models = require 'bumblr/models'  
  require 'bumblr/collections'
  
  class Router extends Backbone.Marionette.AppRouter
    appRoutes:
      'bumblr': 'start'
      'bumblr/settings': 'settings_page'
      'bumblr/dashboard': 'show_dashboard'
      'bumblr/listblogs': 'list_blogs'
      'bumblr/viewblog/:id': 'view_blog'
      'bumblr/addblog' : 'add_new_blog'
      
  current_calendar_date = undefined
  MSGBUS.commands.setHandler 'bumblr:maincalendar:set_date', () ->
    cal = $ '#maincalendar'
    current_calendar_date = cal.fullCalendar 'getDate'

  MSGBUS.reqres.setHandler 'bumblr:maincalendar:get_date', () ->
    current_calendar_date
    
  MSGBUS.commands.setHandler 'bumblr:route', () ->
    console.log "bumblr:route being handled..."
    blog_collection = MSGBUS.reqres.request 'bumblr:get_local_blogs'
    response = blog_collection.fetch()
    response.done =>
      controller = new Controller
      router = new Router
        controller: controller
      console.log 'bumblr router created'
