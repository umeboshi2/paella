define (require, exports, module) ->
  Backbone = require 'backbone'
  MSGBUS = require 'msgbus'
  Marionette = require 'marionette'

  Templates = require 'views/templates'

  FDTemplates = require 'frontdoor/templates'
  
    
  class FrontDoorMainView extends Backbone.Marionette.ItemView
    template: FDTemplates.frontdoor_main

  class SideBarView extends Backbone.Marionette.ItemView
    template: Templates.main_sidebar
    
  module.exports =
    FrontDoorMainView: FrontDoorMainView
    SideBarView: SideBarView
    
    