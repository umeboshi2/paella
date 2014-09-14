define (require, exports, module) ->
  $ = require 'jquery'
  Backbone = require 'backbone'
  Marionette = require 'marionette'
  Util = require 'common/util'
  
  class BaseController extends Backbone.Marionette.Controller
    constructor: (mainbus) ->
      if mainbus != undefined
        @mainbus = mainbus
        @App = @mainbus.reqres.request 'main:app:object'
      else
        console.log "======WARNING Constructing controller with ", mainbus
        
    init_page: () ->
      # do nothing
    scroll_top: Util.scroll_top_fast
    navigate_to_url: Util.navigate_to_url
    navbar_set_active: Util.navbar_set_active
    

  class SideBarController extends BaseController
    make_sidebar: () ->
      @init_page()
      # the model may change
      @App.sidebar.empty()
      view = new @sidebarclass
        model: @sidebar_model
      @App.sidebar.show view

  module.exports =
    BaseController: BaseController
    SideBarController: SideBarController
    
    
  
