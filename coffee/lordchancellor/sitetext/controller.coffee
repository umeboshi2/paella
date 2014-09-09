define (require, exports, module) ->
  $ = require 'jquery'
  Backbone = require 'backbone'
  Marionette = require 'marionette'
  MainBus = require 'msgbus'

  Views = require 'sitetext/views'
  AppBus = require 'sitetext/msgbus'
  require 'sitetext/collections'
    
  { SideBarController } = require 'common/controllers'
  
  #    'sitetext/viewuser/:id': 'view_user'

  side_bar_data = new Backbone.Model
    entries: [
      {
        name: 'List Pages'
        url: '#sitetext/listpages'
      }
      {
        name: 'Add Page'
        url: '#sitetext/addpage'
      }
      ]

  class Controller extends SideBarController
    mainbus: MainBus
    sidebarclass: Views.SideBarView
    sidebar_model: side_bar_data

    make_main_content: ->
      @make_sidebar()
      #@show_page 1
      
    list_pages: ->
      @make_sidebar()
      pages = AppBus.reqres.request 'get-pages'
      response = pages.fetch()
      response.done =>
        view = new Views.PageListView
          collection: pages
        MainBus.vent.trigger 'appregion:content:show', view

    add_page: ->
      @make_sidebar()
      console.log "add_page called on controller"
      view = new Views.NewPageFormView
      MainBus.vent.trigger 'appregion:content:show', view
      
    show_page: (page_id) ->
      @make_sidebar()
      console.log "show_page called on controller"
      page = AppBus.reqres.request 'get-page', page_id
      view = new Views.ShowPageView
        model: page
      MainBus.vent.trigger 'appregion:content:show', view

    edit_page: (page_id) ->
      @make_sidebar()
      page = AppBus.reqres.request 'get-page', page_id
      view = new Views.EditPageView
        model: page
      MainBus.vent.trigger 'appregion:content:show', view
      
    start: ->
      MainBus.vent.trigger 'appregion:content:empty'
      #console.log 'controller.start called'
      @make_main_content()
      #console.log 'wiki started'

  module.exports = Controller
  
