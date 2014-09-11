#
define (require, exports, module) ->
  Backbone = require 'backbone'
  MainBus = require 'msgbus'

  Controller = require 'hubby/controller'
  AppBus = require 'hubby/msgbus'  

  { BootStrapAppRouter } = require 'common/approuters'

  class Router extends BootStrapAppRouter
    appRoutes:
      'hubby': 'start'
      'hubby/viewmeeting/:id': 'show_meeting'
      'hubby/listmeetings': 'list_meetings'
      
  current_calendar_date = undefined
  AppBus.commands.setHandler 'maincalendar:set_date', () ->
    cal = $ '#maincalendar'
    current_calendar_date = cal.fullCalendar 'getDate'

  AppBus.reqres.setHandler 'maincalendar:get_date', () ->
    current_calendar_date
    
  MainBus.commands.setHandler 'hubby:route', () ->
    console.log "hubby:route being handled..."
    controller = new Controller
    router = new Router
      controller: controller
      
