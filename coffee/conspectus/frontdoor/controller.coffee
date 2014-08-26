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
      ]

           
  class Controller extends Backbone.Marionette.Controller
    make_sidebar: ->
      MSGBUS.events.trigger 'sidebar:close'
      view = new FDViews.SideBarView
        model: side_bar_data
      MSGBUS.events.trigger 'sidebar:show', view
      
    make_main_content: ->
      @make_sidebar()
      @show_page 'intro'

    show_page: (name) ->
      @make_sidebar()
      page = MSGBUS.reqres.request 'pages:getpage', name
      response = page.fetch()
      response.done =>
        view = new FDViews.FrontDoorMainView
          model: page
        MSGBUS.events.trigger 'rcontent:show', view
          
    start: ->
      console.log 'controller.start called'
      @make_main_content()
      console.log 'frontdoor started'

  module.exports = Controller
  
