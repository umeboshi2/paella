define (require, exports, module) ->
  $ = require 'jquery'
  Backbone = require 'backbone'
  Marionette = require 'marionette'
  MSGBUS = require 'msgbus'

  Views = require 'bumblr/views'
  Models = require 'bumblr/models'
  
  Collections = require 'bumblr/collections'
  Util = require 'common/util'
  
  fullCalendar = require 'fullcalendar'
  #gcal = require 'fc_gcal'

  sidebar_model = new Backbone.Model
    header: 'Sidebar'
    entries: [
      {
        name: 'mainview-button'
        label: 'Main View'
      }
      {
        name: 'dashboard-view-button'
        label: 'Dashboard'
      }
      {
        name: 'list-blogs-button'
        label: 'List Blogs'
      }
    ]

  meetings = MSGBUS.reqres.request 'hubby:meetinglist'

  credentials = MSGBUS.reqres.request 'bumblr:get_app_settings'
  api_key = credentials.consumer_key
  console.log 'api_key is -> ' + api_key
  window.credentials = credentials    
  class Controller extends Backbone.Marionette.Controller
    make_sidebar: ->
      meetings = MSGBUS.reqres.request 'hubby:meetinglist'
      
      MSGBUS.events.trigger 'sidebar:close'
      view = new Views.SideBarView
        model: sidebar_model
      MSGBUS.events.trigger 'sidebar:show', view
      #if meetings.length == 0
      #  console.log 'fetching pages for sidebar'
      #  meetings.fetch()
      
      
    set_header: (title) ->
      header = $ '#header'
      header.text title
      
    start: ->
      #console.log 'hubby start'
      MSGBUS.events.trigger 'rcontent:close'
      MSGBUS.events.trigger 'sidebar:close'
      @set_header 'Bumblr'
      @show_mainview()

    show_mainview: () ->
      @make_sidebar()
      view = new Views.MainBumblrView
      MSGBUS.events.trigger 'rcontent:show', view
      Util.scroll_top_fast()
      

    show_dashboard: () ->
      @make_sidebar()
      view = new Views.BumblrDashboardView
      MSGBUS.events.trigger 'rcontent:show', view
      Util.scroll_top_fast()
        
    list_blogs: () ->
      console.log 'list_blogs called;'
      @make_sidebar()
      blogs = MSGBUS.reqres.request 'bumblr:get_local_blogs'
      view = new Views.SimpleBlogListView
        collection: blogs
      MSGBUS.events.trigger 'rcontent:show', view
      Util.scroll_top_fast()
      
      
    view_blog: (blog_id) ->
      console.log 'view blog called for ' + blog_id
      @make_sidebar()
      make_collection = 'bumblr:make_blog_post_collection'
      base_hostname = blog_id + '.tumblr.com'
      collection = MSGBUS.reqres.request make_collection, base_hostname
      window.blcollection = collection
      response = collection.fetch()
      response.done =>
        view = new Views.BlogPostListView
          collection: collection
        window.blogView = view
        MSGBUS.events.trigger 'rcontent:show', view
        Util.scroll_top_fast()

    add_new_blog: () ->
      console.log 'add_new_blog called'
      @make_sidebar()
      view = new Views.NewBlogFormView
      MSGBUS.events.trigger 'rcontent:show', view
      Util.scroll_top_fast()
            
  module.exports = Controller
  
