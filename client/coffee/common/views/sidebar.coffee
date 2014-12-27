define (require, exports, module) ->
  Backbone = require 'backbone'
  Marionette = require 'marionette'

  Templates = require 'common/templates'
  { navigate_to_url } = require 'common/util'
  
  class BaseSideBarView extends Backbone.Marionette.ItemView
    template: Templates.main_sidebar
    events:
      'click .sidebar-entry-button': 'sidebar_button_pressed'
      
    sidebar_button_pressed: (event) ->
      #console.log "Sidebar_button_pressed"
      url = event.currentTarget.getAttribute 'button-url'
      navigate_to_url url
      
  module.exports = BaseSideBarView
  