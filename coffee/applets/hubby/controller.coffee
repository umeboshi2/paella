define (require, exports, module) ->
  $ = require 'jquery'
  Backbone = require 'backbone'
  Marionette = require 'marionette'
  MainBus = require 'msgbus'

  Views = require 'hubby/views'
  Models = require 'hubby/models'
  AppBus = require 'hubby/msgbus'
  
  Collections = require 'hubby/collections'

  fullCalendar = require 'fullcalendar'
  { navbar_set_active
    scroll_top_fast } = require 'common/util'

  { SideBarController } = require 'common/controllers'
    
  
  sidebar_model = new Backbone.Model
    entries: [
      {
        url: '#hubby'
        name: 'Main Calendar'
      }
      {
        url: '#hubby/listmeetings'
        name: 'List Meetings'
      }
    ]

  meetings = AppBus.reqres.request 'meetinglist'

  prepare_slideshow_meeting_items = (meeting) ->
    pages = []
    agenda_section = 'start'
    item_count = 0
    meeting_items = meeting.meeting_items
    if meeting_items?
      for mitem in meeting_items
        item_count += 1
        item = meeting.items[mitem.item_id]
        if mitem.type != agenda_section and mitem.type
          agenda_section = mitem.type
        
  class Controller extends SideBarController
    mainbus: MainBus
    sidebarclass: Views.SideBarView
    sidebar_model: sidebar_model
      
    set_header: (title) ->
      header = $ '#header'
      header.text title
      
    start: ->
      #console.log 'hubby start'
      MainBus.vent.trigger 'appregion:content:empty'
      MainBus.vent.trigger 'appregion:sidebar:empty'
      @set_header 'Hubby'
      @show_calendar()
      
    show_calendar: () ->
      #console.log 'hubby show calendar'
      @make_sidebar()
      view = new Views.MeetingCalendarView
      MainBus.vent.trigger 'appregion:content:show', view
      scroll_top_fast()
      
    show_meeting: (meeting_id) ->
      #console.log 'show_meeting called'
      @make_sidebar()
      meeting = new Models.MainMeetingModel
        id: meeting_id
      response = meeting.fetch()
      response.done =>
        view = new Views.ShowMeetingView
          model: meeting
        MainBus.vent.trigger 'appregion:content:show', view
      scroll_top_fast()

    list_meetings: () ->
      #console.log 'list_meetings called'
      @make_sidebar()
      view = new Views.MeetingListView
        collection: meetings
      if meetings.length == 0
        meetings.fetch()
      MainBus.vent.trigger 'appregion:content:show', view
      scroll_top_fast()
      
  module.exports = Controller
  
