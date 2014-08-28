define (require, exports, module) ->
  $ = require 'jquery'
  Backbone = require 'backbone'
  Marionette = require 'marionette'
  MSGBUS = require 'msgbus'

  Views = require 'hubby/views'
  Models = require 'hubby/models'
  
  Collections = require 'hubby/collections'

  fullCalendar = require 'fullcalendar'
  { navbar_set_active } = require 'common/util'
  
  
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

  meetings = MSGBUS.reqres.request 'hubby:meetinglist'
  
  class Controller extends Backbone.Marionette.Controller
    make_sidebar: ->
      navbar_set_active '#hubby'
      MSGBUS.events.trigger 'sidebar:close'
      view = new Views.SideBarView
        model: sidebar_model
      MSGBUS.events.trigger 'sidebar:show', view
      
    set_header: (title) ->
      header = $ '#header'
      header.text title
      
    start: ->
      #console.log 'hubby start'
      MSGBUS.events.trigger 'rcontent:close'
      MSGBUS.events.trigger 'sidebar:close'
      @set_header 'Hubby'
      @show_calendar()
      
    show_calendar: () ->
      #console.log 'hubby show calendar'
      @make_sidebar()
      view = new Views.MeetingCalendarView
      MSGBUS.events.trigger 'rcontent:show', view
      
    show_meeting: (meeting_id) ->
      #console.log 'show_meeting called'
      @make_sidebar()
      meeting = new Models.MainMeetingModel
        id: meeting_id
      response = meeting.fetch()
      response.done =>
        view = new Views.ShowMeetingView
          model: meeting
        MSGBUS.events.trigger 'rcontent:show', view

    list_meetings: () ->
      console.log 'list_meetings called'
      @make_sidebar()
      view = new Views.MeetingListView
        collection: meetings
      if meetings.length == 0
        meetings.fetch()
      MSGBUS.events.trigger 'rcontent:show', view
      
    edit_page: (page_id) ->
      @make_sidebar()
      page = MSGBUS.reqres.request 'wiki:pagecontent', page_id
      view = new Views.EditPageView
        model: page
      MSGBUS.events.trigger 'rcontent:show', view
      
      
              
  module.exports = Controller
  
