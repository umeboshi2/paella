#
define (require, exports, module) ->
  Backbone = require 'backbone'
  MSGBUS = require 'msgbus'

  Controller = require 'demoapp/controller'
  

  class Router extends Backbone.Marionette.AppRouter
    appRoutes:
      'demoapp': 'start'
      'demoapp/viewmeeting/:id': 'show_meeting'
      'demoapp/listmeetings': 'list_meetings'
      
  current_calendar_date = undefined
  MSGBUS.commands.setHandler 'demoapp:maincalendar:set_date', () ->
    cal = $ '#maincalendar'
    current_calendar_date = cal.fullCalendar 'getDate'

  MSGBUS.reqres.setHandler 'demoapp:maincalendar:get_date', () ->
    current_calendar_date
    
  MSGBUS.commands.setHandler 'demoapp:route', () ->
    #window.msgbus = MSGBUS
    console.log "demoapp:route being handled..."
    controller = new Controller
    router = new Router
      controller: controller
      
