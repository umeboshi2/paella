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
  #gcal = require 'fc_gcal'

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
  api_key = credentials.consumer_key
  console.log 'api_key is -> ' + api_key
  window.credentials = credentials    
  class Controller extends Backbone.Marionette.Controller
    make_sidebar: ->
      Util.navbar_set_active '#bumblr'
      MainBus.vent.trigger 'sidebar:close'
      view = new Views.SideBarView
        model: side_bar_data
      MainBus.vent.trigger 'sidebar:show', view
      
    set_header: (title) ->
      header = $ '#header'
      header.text title
      
    start: ->
      MainBus.vent.trigger 'rcontent:close'
      MainBus.vent.trigger 'sidebar:close'
      @set_header 'Bumblr'
      @list_blogs()
      
    show_mainview: () ->
      @make_sidebar()
      view = new Views.MainBumblrView
      MainBus.vent.trigger 'rcontent:show', view
      Util.scroll_top_fast()
      

    show_dashboard: () ->
      @make_sidebar()
      view = new Views.BumblrDashboardView
      MainBus.vent.trigger 'rcontent:show', view
      Util.scroll_top_fast()
        
    list_blogs: () ->
      #console.log 'list_blogs called;'
      @make_sidebar()
      blogs = AppBus.reqres.request 'get_local_blogs'
      view = new Views.SimpleBlogListView
        collection: blogs
      MainBus.vent.trigger 'rcontent:show', view
      Util.scroll_top_fast()
      
      
    view_blog: (blog_id) ->
      #console.log 'view blog called for ' + blog_id
      @make_sidebar()
      make_collection = 'make_blog_post_collection'
      base_hostname = blog_id + '.tumblr.com'
      collection = AppBus.reqres.request make_collection, base_hostname
      window.blcollection = collection
      response = collection.fetch()
      response.done =>
        view = new Views.BlogPostListView
          collection: collection
        window.blogView = view
        MainBus.vent.trigger 'rcontent:show', view
        Util.scroll_top_fast()

    add_new_blog: () ->
      #console.log 'add_new_blog called'
      @make_sidebar()
      view = new Views.NewBlogFormView
      MainBus.vent.trigger 'rcontent:show', view
      Util.scroll_top_fast()
            
    settings_page: () ->
      #console.log 'Settings page.....'
      settings = AppBus.reqres.request 'get_app_settings'
      view = new Views.ConsumerKeyFormView model:settings
      MainBus.vent.trigger 'rcontent:show', view
      Util.scroll_top_fast()
      
  module.exports = Controller
  
