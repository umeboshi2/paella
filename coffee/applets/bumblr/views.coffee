define (require, exports, module) ->
  Backbone = require 'backbone'
  MainBus = require 'msgbus'
  Marionette = require 'marionette'
  Masonry = require 'masonry'
  imagesLoaded = require 'imagesloaded'

  FormView = require 'common/views/formview'
  Templates = require 'bumblr/templates'
  Models = require 'bumblr/models'
  AppBus = require 'bumblr/msgbus'
  
  BaseModels = require 'models'
  BaseSideBarView = require 'common/views/sidebar'
  require 'jquery-ui'

  { navigate_to_url } = require 'common/util'

  class SideBarView extends BaseSideBarView
      
  class SimpleBlogInfoView extends Backbone.Marionette.ItemView
    template: Templates.simple_blog_info

  class SimpleBlogListView extends Backbone.Marionette.CompositeView
    childView: SimpleBlogInfoView
    template: Templates.simple_blog_list
    childViewContainer: '#bloglist-container'
    ui:
      blogs: '#bloglist-container'
      
    onDomRefresh: () ->
      console.log 'onDomRefresh called on SimpleBlogListView'
      @masonry = new Masonry "#bloglist-container",
        gutter: 2
        isInitLayout: false
        itemSelector: '.blog'
        columnWidth: 100
      delete_buttons = $ '.delete-blog-button'
      delete_buttons.on 'click', (event) =>
        target = $ event.currentTarget
        blog = target.attr 'blog'
        id = "#{blog}.tumblr.com"
        model = @collection.get id
        model.destroy()
        #console.log "Delete #{blog}"
        @masonry.reloadItems()
        @masonry.layout()
      @set_layout()
      
    set_layout: ->
      @masonry.reloadItems()
      @masonry.layout()
        
  class NewBlogFormView extends FormView
    template: Templates.new_blog_form_view
    ui:
      blog_name: '[name="blog_name"]'

    updateModel: ->
      #console.log 'updateModel'
      @collection = AppBus.reqres.request 'get_local_blogs'
      @model = @collection.add_blog @ui.blog_name.val()

    onSuccess: ->
      #console.log 'onSuccess called'
      navigate_to_url '#bumblr/listblogs'
  
    createModel: ->
      return new Backbone.Model url:'/'
      
        
                
  class MainBumblrView extends Backbone.Marionette.ItemView
    template: Templates.main_bumblr_view

  class BumblrDashboardView extends Backbone.Marionette.ItemView
    template: Templates.bumblr_dashboard_view
    
  class ShowPageView extends Backbone.Marionette.ItemView
    template: Templates.page_view


  class SimpleBlogPostView extends Backbone.Marionette.ItemView
    template: Templates.simple_post_view
    #className: 'col-sm-10'
    className: 'post'
    
    
  class BlogPostListView extends Backbone.Marionette.CompositeView
    template: Templates.simple_post_page_view
    childView: SimpleBlogPostView
    childViewContainer: '#posts-container'
    ui:
      posts: '#posts-container'
      slideshow_button: '#slideshow-button'
      
    #className: 'row'
    events:
      'click #next-page-button': 'get_next_page'
      'click #prev-page-button': 'get_prev_page'
      'click #slideshow-button': 'manage_slideshow'

    keycommands:
      prev: 65
      next: 90
      

    manage_slideshow: () ->
      button = @ui.slideshow_button
      if button.hasClass 'fa-play'
        @start_slideshow()
      else
        @stop_slideshow()
        
    
    start_slideshow: () ->
      console.log "start slideshow"
      @slideshow_handler = setInterval =>
        console.log "getting next page"
        @get_next_page()
      , 6000
      @ui.slideshow_button.removeClass 'fa-play'
      @ui.slideshow_button.addClass 'fa-stop'
      
    
    stop_slideshow: () ->
      clearInterval @slideshow_handler
      @ui.slideshow_button.removeClass 'fa-stop'
      @ui.slideshow_button.addClass 'fa-play'
      
    get_next_page: () ->
      @ui.posts.hide()
      response = @collection.getNextPage()
      response.done =>
        @set_image_layout()
        #@ui.posts.show()
        
    get_prev_page: () ->
      response = @collection.getPreviousPage()
      response.done =>
        @set_image_layout()

    get_another_page: (direction) ->
      @ui.posts.hide()
      switch direction
        when 'prev' then response = @collection.getPreviousPage()
        when 'next' then response = @collection.getNextPage()
        else response = null
      if response
        response.done =>
          @set_image_layout()
          

    handle_key_command: (command) ->
      #console.log "handle_key_command #{command}"
      if command in ['prev', 'next']
        @get_another_page command
      
    keydownHandler: (event_object) =>
      #console.log 'keydownHandler ' + event_object
      for key, value of @keycommands
        if event_object.keyCode == value
          @handle_key_command key
      
    set_image_layout: ->
      items = $ '.post'
      imagesLoaded items, =>
        @ui.posts.show()
        #console.log "Images Loaded>.."
        @masonry.reloadItems()
        @masonry.layout()      
  
    onRenderTemplate: ->
      #console.log 'onRenderTemplate'
      
    onRenderCollection: ->
      #console.log 'onRenderCollection'

    onRender: ->
      #console.log 'onRender'
      
    onDomRefresh: () ->
      console.log 'onDomRefresh called on BlogPostListView'
      $('html').keydown @keydownHandler
      @masonry = new Masonry "#posts-container",
        gutter: 2
        isInitLayout: false
        itemSelector: '.post'
      @set_image_layout()

    onBeforeDestroy: () ->
      #console.log "Remove @keydownHandler" + @keydownHandler
      $('html').unbind 'keydown', @keydownHandler
      @stop_slideshow()
      
      
  class ConsumerKeyFormView extends FormView
    template: Templates.consumer_key_form
    ui:
      consumer_key: '[name="consumer_key"]'
      consumer_secret: '[name="consumer_secret"]'
      token: '[name="token"]'
      token_secret: '[name="token_secret"]'

    updateModel: ->
      @model.set
        consumer_key: @ui.consumer_key.val()
        consumer_secret: @ui.consumer_secret.val()
        token: @ui.token.val()
        token_secret: @ui.token_secret.val()
        
    createModel: ->
      AppBus.reqres.request 'get_app_settings'
        
    onSuccess: (model) ->
      #console.log 'onSuccess called'
      navigate_to_url '#bumblr'
      
  module.exports =
    SideBarView: SideBarView
    MainBumblrView: MainBumblrView
    BumblrDashboardView: BumblrDashboardView
    SimpleBlogListView: SimpleBlogListView
    BlogPostListView: BlogPostListView
    NewBlogFormView: NewBlogFormView
    ConsumerKeyFormView: ConsumerKeyFormView
    
    
