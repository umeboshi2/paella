define (require, exports, module) ->
  $ = require 'jquery'
  Backbone = require 'backbone'
  Marionette = require 'marionette'
  MainBus = require 'msgbus'

  Views = require 'bumblr/views'
  Models = require 'bumblr/models'
  AppBus = require 'bumblr/msgbus'
    
  Collections = require 'bumblr/collections'
  Util = require 'common/util'
  
  fullCalendar = require 'fullcalendar'

  { SideBarController } = require 'common/controllers'

  side_bar_data = new Backbone.Model
    entries: [
      {
        name: 'List Blogs'
        url: '#bumblr/listblogs'
      }
      {
        name: 'Settings'
        url: '#bumblr/settings'
      }
      ]

  credentials = AppBus.reqres.request 'get_app_settings'
  api_key = credentials.get 'consumer_key'
  #console.log 'api_key is -> ' + api_key
  
  class Controller extends SideBarController
    sidebarclass: Views.SideBarView
    sidebar_model: side_bar_data
    
    init_page: ->
      #console.log 'init_page', @App
      view = new Views.BlogModal()
      @App.modal.show view
      
    set_header: (title) ->
      header = $ '#header'
      header.text title
      
    start: ->
      if @App.content.hasView()
        console.log 'empty content....'
        @App.content.empty()
      if @App.sidebar.hasView()
        console.log 'empty sidebar....'
        @App.sidebar.empty()
      @set_header 'Bumblr'
      @list_blogs()
      
    show_mainview: () ->
      @make_sidebar()
      view = new Views.MainBumblrView
      @App.content.show view
      Util.scroll_top_fast()
      

    show_dashboard: () ->
      @make_sidebar()
      view = new Views.BumblrDashboardView
      @App.content.show view
      Util.scroll_top_fast()
        
    list_blogs: () ->
      #console.log 'list_blogs called;'
      @make_sidebar()
      blogs = AppBus.reqres.request 'get_local_blogs'
      view = new Views.SimpleBlogListView
        collection: blogs
      @App.content.show view
      Util.scroll_top_fast()
      
      
    view_blog: (blog_id) ->
      #console.log 'view blog called for ' + blog_id
      @make_sidebar()
      make_collection = 'make_blog_post_collection'
      base_hostname = blog_id + '.tumblr.com'
      collection = AppBus.reqres.request make_collection, base_hostname
      response = collection.fetch()
      response.done =>
        view = new Views.BlogPostListView
          collection: collection
        @App.content.show view
        Util.scroll_top_fast()

    add_new_blog: () ->
      #console.log 'add_new_blog called'
      @make_sidebar()
      view = new Views.NewBlogFormView
      @App.content.show view
      Util.scroll_top_fast()
            
    settings_page: () ->
      #console.log 'Settings page.....'
      settings = AppBus.reqres.request 'get_app_settings'
      view = new Views.ConsumerKeyFormView model:settings
      @App.content.show view
      Util.scroll_top_fast()
      
  module.exports = Controller
  
