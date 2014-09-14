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
    pages: AppBus.reqres.request 'get-pages'
    make_main_content: ->
      @make_sidebar()
      #@show_page 1
      
    list_pages: ->
      @make_sidebar()
      response = @pages.fetch()
      response.done =>
        view = new Views.PageListView
          collection: @pages
        @App.content.show view

    add_page: ->
      @make_sidebar()
      #console.log "add_page called on controller"
      view = new Views.NewPageFormView
      @App.content.show view

    _show_page: (page) ->
      #window.showpage = page
      #console.log "_show_page for #{page} called on controller"
      #console.log page
      view = new Views.ShowPageView
        model: page
      @App.content.show view
      
    show_page: (name) ->
      @make_sidebar()
      # we do this if/else in case this url is called
      # as the entry point.  This should probably be
      # generalized in a base controller class. 
      # we should probably check for length of pages
      if not @App.content.hasView()
        @App.content.empty()
        response = @pages.fetch()
        response.done =>
          page = @pages.get name
          @_show_page page
      else
        page = AppBus.reqres.request 'get-page', name
        @_show_page page
      
    edit_page: (name) ->
      @make_sidebar()
      #console.log "Get page named #{name} for editing"
      page = AppBus.reqres.request 'get-page', name
      #console.log "Here is the page #{page}"
      view = new Views.EditPageView
        model: page
      @App.content.show view
      
    start: ->
      if @App.content.hasView()
        @App.content.empty()
      #console.log 'controller.start called'
      @make_main_content()
      #console.log 'wiki started'

  module.exports = Controller
  
