define (require, exports, module) ->
  Backbone = require 'backbone'
  MSGBUS = require 'msgbus'
  Marionette = require 'marionette'

  Templates = require 'views/templates'

  FDTemplates = require 'frontdoor/templates'
  SiteTemplates = require 'common/templates/site'
  
  class LoginView extends Backbone.Marionette.ItemView
    template: Templates.login_form
    
  class FrontDoorMainView extends Backbone.Marionette.ItemView
    template: FDTemplates.frontdoor_main

  class SideBarView extends Backbone.Marionette.ItemView
    template: SiteTemplates.main_sidebar
    
  module.exports =
    LoginView: LoginView
    FrontDoorMainView: FrontDoorMainView
    SideBarView: SideBarView
    
    