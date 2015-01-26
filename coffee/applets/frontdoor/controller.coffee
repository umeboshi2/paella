define (require, exports, module) ->
  $ = require 'jquery'
  Backbone = require 'backbone'
  Marionette = require 'marionette'
  marked = require 'marked'
  Util = require 'common/util'

  MainBus = require 'msgbus'
  Models = require 'models'
  Collections = require 'collections'

  AppBus = require 'frontdoor/msgbus'
  Views = require 'frontdoor/views'

  

  { SideBarController } = require 'common/controllers'

  pages = MainBus.reqres.request 'pages:collection'
  window.docsss = pages
  
  side_bar_data = new Backbone.Model
    entries: [
      {
        name: 'News'
        url: '#pages/news'
      }
      {
        name: 'Introduction'
        url: '#pages/intro'
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
        name: 'Debian Installer'
        url: '#pages/debian-install'
      }
      {
        name: 'History'
        url: '#pages/history'
      }
      ]

           
  class Controller extends SideBarController
    mainbus: MainBus
    sidebarclass: Views.SideBarView
    sidebar_model: side_bar_data
      
    make_main_content: ->
      @make_sidebar()
      @show_page 'intro'

    show_page: (name) ->
      @make_sidebar()
      console.log "getting page #{name}"
      page = MainBus.reqres.request 'pages:getpage', name
      window.mypage = page
      response = page.fetch()
      response.done =>
        view = new Views.FrontDoorMainView
          model: page
        @App.content.show view
      Util.scroll_top_fast()
      
    start: ->
      #console.log 'controller.start called'
      @make_main_content()
      #console.log 'frontdoor started'

    list_pages: ->
      @make_sidebar()
      pages = AppBus.reqres.request 'pages:collection'
      response = pages.fetch()
      response.done =>
        view = new Views.PageListView
          collection: pages
        @App.content.show view
        
  module.exports = Controller
  
