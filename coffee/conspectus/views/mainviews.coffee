define (require, exports, module) ->
  Backbone = require 'backbone'
  MSGBUS = require 'msgbus'
  Marionette = require 'marionette'

  Templates = require 'views/templates'
  
  MSGBUS.reqres.setHandler 'hubby:navbar-color', ->
    navbar = $ '#main-navbar'
    navbar.css 'color'
    
  MSGBUS.reqres.setHandler 'hubby:navbar-bg-color', ->
    navbar = $ '#main-navbar'
    navbar.css 'background-color'
    

  MSGBUS.reqres.setHandler  
  class MainPageView extends Backbone.Marionette.ItemView
    template: Templates.PageLayoutTemplate

  class MainPageLayout extends Backbone.Marionette.LayoutView
    template: Templates.BootstrapLayoutTemplate
    
  class MainHeaderView extends Backbone.Marionette.ItemView
    template: Templates.main_header
    
  class BootstrapNavBarView extends Backbone.Marionette.ItemView
    template: Templates.BootstrapNavBarTemplate
        
  
  module.exports =
    MainPageView: MainPageView
    MainPageLayout: MainPageLayout
    MainHeaderView: MainHeaderView
    BootstrapNavBarView: BootstrapNavBarView
    
  