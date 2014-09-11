define (require, exports, module) ->
  Backbone = require 'backbone'
  Marionette = require 'marionette'
  
  Models = require 'models'
  Templates = require 'common/templates'

  FDTemplates = require 'frontdoor/templates'
  FormView = require 'common/views/formview'
  { navigate_to_url } = require 'common/util'
    
  BaseEditPageView = require 'common/views/editor'
  BaseSideBarView = require 'common/views/sidebar'
    
  class FrontDoorMainView extends Backbone.Marionette.ItemView
    template: FDTemplates.frontdoor_main

  class SideBarView extends BaseSideBarView
    
  module.exports =
    FrontDoorMainView: FrontDoorMainView
    SideBarView: SideBarView
