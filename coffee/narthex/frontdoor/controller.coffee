define (require, exports, module) ->
  $ = require 'jquery'
  Backbone = require 'backbone'
  Marionette = require 'marionette'
  MainBus = require 'msgbus'

  Views = require 'frontdoor/views'
  marked = require 'marked'
  Models = require 'models'
  Collections = require 'collections'

  Util = require 'common/util'

  { SideBarController } = require 'common/controllers'

  side_bar_data = new Backbone.Model
    entries: [
      {
        name: 'Home'
        url: '#'
      }
      ]

  class Controller extends SideBarController
    mainbus: MainBus
    sidebarclass: Views.SideBarView
    sidebar_model: side_bar_data
      
    make_main_content: ->
      @make_sidebar()
      page = new Backbone.Model
        content: 'hello there'
      view = new Views.FrontDoorMainView
        model: page
      MainBus.vent.trigger 'rcontent:show', view
      
    show_page: (name) ->
      @make_sidebar()
      #response = page.fetch()
      #response.done =>
      view = new Views.FrontDoorMainView
        model: page
      MainBus.vent.trigger 'rcontent:show', view

    start: ->
      #console.log 'controller.start called'
      @make_main_content()
      #console.log 'frontdoor started'

  module.exports = Controller
  
