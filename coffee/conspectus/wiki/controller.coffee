define (require, exports, module) ->
  $ = require 'jquery'
  Backbone = require 'backbone'
  Marionette = require 'marionette'
  MainBus = require 'msgbus'

  FDViews = require 'wiki/views'
  AppBus = require 'wiki/msgbus'
  
  marked = require 'marked'
  Models = require 'models'
  Collections = require 'collections'
  
  { navbar_set_active } = require 'common/util'


  side_bar_data = new Backbone.Model
    entries: [
      {
        name: 'Home'
        url: '#'
      }
      {
        name: 'News'
        url: '#wiki/showpage/news'
      }
      {
        name: 'List Pages'
        url: '#wiki/listpages'
      }
      ]

           
  class Controller extends Backbone.Marionette.Controller
    make_sidebar: ->
      navbar_set_active '#wiki'
      MainBus.vent.trigger 'sidebar:close'
      view = new FDViews.SideBarView
        model: side_bar_data
      MainBus.vent.trigger 'sidebar:show', view
      
    make_main_content: ->
      @make_sidebar()
      @show_page 'intro'

    list_pages: ->
      @make_sidebar()
      pages = AppBus.reqres.request 'pages:collection'
      response = pages.fetch()
      response.done =>
        view = new FDViews.PageListView
          collection: pages
        MainBus.vent.trigger 'rcontent:show', view
      window.pages = pages
      
    show_page: (name) ->
      @make_sidebar()
      page = AppBus.reqres.request 'pages:getpage', name
      #response = page.fetch()
      #response.done =>
      view = new FDViews.FrontDoorMainView
        model: page
      MainBus.vent.trigger 'rcontent:show', view

    edit_page: (name) ->
      @make_sidebar()
      page = AppBus.reqres.request 'pages:getpage', name
      window.current_page = page
      view = new FDViews.EditPageView
        model: page
      MainBus.vent.trigger 'rcontent:show', view

    add_page: () ->
      @make_sidebar()
      view = new FDViews.NewPageFormView
      MainBus.vent.trigger 'rcontent:show', view
      
      
    start: ->
      #console.log 'controller.start called'
      @make_main_content()
      #console.log 'wiki started'

  module.exports = Controller
  
