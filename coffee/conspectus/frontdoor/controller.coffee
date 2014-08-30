define (require, exports, module) ->
  $ = require 'jquery'
  Backbone = require 'backbone'
  Marionette = require 'marionette'
  MainBus = require 'msgbus'

  FDViews = require 'frontdoor/views'
  WikiBus = require 'wiki/msgbus'

  marked = require 'marked'
  Models = require 'models'
  Collections = require 'collections'

  Util = require 'common/util'

  side_bar_data = new Backbone.Model
    entries: [
      {
        name: 'Home'
        url: '#'
      }
      {
        name: 'Wiki'
        url: '#wiki'
      }
      {
        name: 'Bumblr'
        url: '#bumblr'
      }
      {
        name: 'Hubby'
        url: '#hubby'
      }
      ]

           
  class Controller extends Backbone.Marionette.Controller
    make_sidebar: ->
      MainBus.vent.trigger 'sidebar:close'
      view = new FDViews.SideBarView
        model: side_bar_data
      MainBus.vent.trigger 'sidebar:show', view
      
    make_main_content: ->
      @make_sidebar()
      @show_page 'intro'

    show_page: (name) ->
      @make_sidebar()
      page = WikiBus.reqres.request 'pages:getpage', name
      #response = page.fetch()
      #response.done =>
      view = new FDViews.FrontDoorMainView
        model: page
      MainBus.vent.trigger 'rcontent:show', view

    start: ->
      #console.log 'controller.start called'
      @make_main_content()
      #console.log 'frontdoor started'

  module.exports = Controller
  
