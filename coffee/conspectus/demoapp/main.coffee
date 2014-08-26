#
define (require, exports, module) ->
  Backbone = require 'backbone'
  MSGBUS = require 'msgbus'

  Controller = require 'demoapp/controller'
  

  class Router extends Backbone.Marionette.AppRouter
    appRoutes:
      'hubby': 'start'
      'hubby/viewmeeting/:id': 'show_meeting'
      'hubby/listmeetings': 'list_meetings'
      
  current_calendar_date = undefined
  MSGBUS.commands.setHandler 'hubby:maincalendar:set_date', () ->
    cal = $ '#maincalendar'
    current_calendar_date = cal.fullCalendar 'getDate'

  MSGBUS.reqres.setHandler 'hubby:maincalendar:get_date', () ->
    current_calendar_date
    
  MSGBUS.commands.setHandler 'hubby:route', () ->
    #window.msgbus = MSGBUS
    console.log "hubby:route being handled..."
    controller = new Controller
    router = new Router
      controller: controller
      
