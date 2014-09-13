define (require, exports, module) ->
  Backbone = require 'backbone'
  Marionette = require 'marionette'

  Templates = require 'common/templates'

  class MainPageLayout extends Backbone.Marionette.LayoutView
    template: Templates.BootstrapLayoutTemplate

  class BootstrapNoGridLayout extends Backbone.Marionette.LayoutView
    template: Templates.BootstrapNoGridLayoutTemplate
    
  class BootstrapNavBarView extends Backbone.Marionette.ItemView
    template: Templates.BootstrapNavBarTemplate
        
  class LoginView extends Backbone.Marionette.ItemView
    template: Templates.login_form

  class UserMenuView extends Backbone.Marionette.ItemView
    template: Templates.user_menu
    
  module.exports =
    MainPageLayout: MainPageLayout
    BootstrapNoGridLayout: BootstrapNoGridLayout
    BootstrapNavBarView: BootstrapNavBarView
    LoginView: LoginView
    UserMenuView: UserMenuView
      
