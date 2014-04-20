define (require, exports, module) ->
  $ = require 'jquery'
  Backbone = require 'backbone'
  Marionette = require 'marionette'
  MSGBUS = require 'msgbus'

  FDViews = require 'frontdoor/views'

  marked = require 'marked'
  Models = require 'models'
  Collections = require 'collections'
  
  side_bar_data = new Backbone.Model
    entries: [
      {
        name: 'Home'
        url: '#'
      }
      {
        name: 'News'
        url: '#pages/news'
      }
      {
        name: 'Todo List'
        url: '#pages/todo'
      }
      {
        name: 'Vagrant'
        url: '#pages/vagrant'
      }
      {
        name: 'Install Procedure'
        url: '#pages/install-procedure'
      }
      {
        name: 'Live Debian System'
        url: '#pages/live-system'
      }
      {
        name: 'PXE Issues'
        url: '#pages/pxe-issues'
      }
      {
        name: 'Pillar Data'
        url: '#pages/pillar-data'
      }
      {
        name: 'System UUID'
        url: '#pages/system-uuid'
      }
      {
        name: 'Debian Preseed'
        url: '#pages/preseed'
      }
      {
        name: 'History'
        url: '#pages/history'
      }
      ]

           
  
  class Controller extends Backbone.Marionette.Controller
    make_sidebar: ->
      MSGBUS.events.trigger 'sidebar:close'
      view = new FDViews.SideBarView
        model: side_bar_data
      MSGBUS.events.trigger 'sidebar:show', view
      
    make_main_content: ->
      @show_page 'intro'

    show_page: (name) ->
      @make_sidebar()
      #content = require 'text!../../../../pages/' + name
      page = MSGBUS.reqres.request 'pages:getpage', name
      response = page.fetch()
      response.done =>
        view = new FDViews.FrontDoorMainView
          model: page
        MSGBUS.events.trigger 'rcontent:show', view
        $('html, body').animate {scrollTop: 0}, 'fast'
          
    start: ->
      @make_main_content()
      console.log 'frontdoor started'
        

  module.exports = Controller
  
