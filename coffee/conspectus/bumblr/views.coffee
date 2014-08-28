define (require, exports, module) ->
  Backbone = require 'backbone'
  MSGBUS = require 'msgbus'
  Marionette = require 'marionette'

  FormView = require 'common/views/formview'
  Templates = require 'bumblr/templates'
  Models = require 'bumblr/models'
  BaseModels = require 'models'
  BaseSideBarView = require 'common/views/sidebar'
  require 'jquery-ui'

  class SideBarView extends BaseSideBarView
      
      
  render_calendar_event = (calEvent, element) ->
    calEvent.url = '#bumblr/viewmeeting/' + calEvent.id
    element.css
      'font-size' : '0.9em'

  calendar_view_render = (view, element) ->
    MSGBUS.commands.execute 'bumblr:maincalendar:set_date'

  loading_calendar_events = (bool) ->
    loading = $ '#loading'
    header = $ '.fc-header'
    if bool
      loading.show()
      header.hide()
    else
      loading.hide()
      header.show()
      

  class SimpleBlogInfoView extends Backbone.Marionette.ItemView
    template: Templates.simple_blog_info

  class SimpleBlogListView extends Backbone.Marionette.CompositeView
    childView: SimpleBlogInfoView
    template: Templates.simple_blog_list
    
  class NewBlogFormView extends FormView
    template: Templates.new_blog_form_view
    ui:
      blog_name: '[name="blog_name"]'

    updateModel: ->
      console.log 'updateModel'
      @collection = MSGBUS.reqres.request 'bumblr:get_local_blogs'
      console.log 'window.blcollection set'
      @model = @collection.add_blog @ui.blog_name.val()

    saveModel: ->
      console.log 'called saveModel'
      @model.save()
      
    onSuccess: ->
      console.log 'onSuccess called'
      r = new Backbone.Router
      r.navigate '#bumblr/listblogs', trigger:true
  
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
    className: 'col-sm-5'
    #tagName: 'span'
    
  class BlogPostListView extends Backbone.Marionette.CompositeView
    template: Templates.simple_post_page_view
    childView: SimpleBlogPostView
    className: 'row'
    events:
      'click #next-page-button': 'get_next_page'
      'click #prev-page-button': 'get_prev_page'

    get_next_page: () ->
      @collection.getNextPage()

    get_prev_page: () ->
      @collection.getPreviousPage()

    onDomRefresh: () ->
      console.log 'onDomRefresh called on BlogPostListView'
      container = $ 'body'
      window.container = container
      container.keydown (event_object) =>
        console.log 'keydown' + event_object
        window.eo = event_object
        if event_object.keyCode == 65
          @get_prev_page()
        if event_object.keyCode == 90
          @get_next_page()

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
      MSGBUS.reqres.request 'bumblr:get_app_settings'
        

  module.exports =
    SideBarView: SideBarView
    MainBumblrView: MainBumblrView
    BumblrDashboardView: BumblrDashboardView
    SimpleBlogListView: SimpleBlogListView
    BlogPostListView: BlogPostListView
    NewBlogFormView: NewBlogFormView
    ConsumerKeyFormView: ConsumerKeyFormView
    
    