define (require, exports, module) ->
  $ = require 'jquery'
  Backbone = require 'backbone'
  Marionette = require 'marionette'
  MainBus = require 'msgbus'

  Views = require 'wiki/views'
  AppBus = require 'wiki/msgbus'
  
  { SideBarController } = require 'common/controllers'
  

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

  class Controller extends SideBarController
    mainbus: MainBus
    sidebarclass: Views.SideBarView
    sidebar_model: side_bar_data

    make_main_content: ->
      @make_sidebar()
      @show_page 'intro'

    list_pages: ->
      @make_sidebar()
      pages = AppBus.reqres.request 'pages:collection'
      response = pages.fetch()
      response.done =>
        view = new Views.PageListView
          collection: pages
        @App.content.show view
        
    show_page: (name) ->
      @make_sidebar()
      page = AppBus.reqres.request 'pages:getpage', name
      view = new Views.FrontDoorMainView
        model: page
      @App.content.show view
  
    edit_page: (name) ->
      @make_sidebar()
      page = AppBus.reqres.request 'pages:getpage', name
      view = new Views.EditPageView
        model: page
      @App.content.show view

    add_page: () ->
      @make_sidebar()
      view = new Views.NewPageFormView
      @App.content.show view
      
      
    start: ->
      #console.log 'controller.start called'
      @make_main_content()
      #console.log 'wiki started'

  module.exports = Controller
  
