define (require, exports, module) ->
  $ = require 'jquery'
  Backbone = require 'backbone'
  Marionette = require 'marionette'
  Util = require 'common/util'
  
  class BaseController extends Backbone.Marionette.Controller
    init_page: () ->
      # do nothing
    scroll_top: Util.scroll_top_fast
    navigate_to_url: Util.navigate_to_url
    navbar_set_active: Util.navbar_set_active
    

  class SideBarController extends BaseController
    make_sidebar: () ->
      @init_page()
      @mainbus.vent.trigger 'sidebar:close'
      view = new @sidebarclass
        model: @sidebar_model
      @mainbus.vent.trigger 'sidebar:show', view
      
  module.exports =
    BaseController: BaseController
    SideBarController: SideBarController
    
    
  
