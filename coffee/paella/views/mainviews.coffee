define (require, exports, module) ->
  Backbone = require 'backbone'
  MSGBUS = require 'msgbus'
  Marionette = require 'marionette'

  SiteTemplates = require 'common/templates/site'
  
  Menus = require 'common/templates/menus'
  
  class MenuView extends Backbone.Marionette.ItemView
    template: Menus.make_menu

  class UserMenuView extends Backbone.Marionette.ItemView
    template: SiteTemplates.user_menu
        
  class MainBarView extends Backbone.Marionette.ItemView
    template: SiteTemplates.main_bar

  class MainPageView extends Backbone.Marionette.ItemView
    template: SiteTemplates.PageLayoutTemplate

  class MainPageLayout extends Backbone.Marionette.Layout
    template: SiteTemplates.PageLayoutTemplate
    
    
  
  module.exports =
    MenuView: MenuView
    MainBarView: MainBarView
    MainPageView: MainPageView
    MainPageLayout: MainPageLayout
    UserMenuView: UserMenuView
    
  