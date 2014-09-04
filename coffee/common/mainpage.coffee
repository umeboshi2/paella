define (require, exports, module) ->
  Backbone = require 'backbone'
  Marionette = require 'marionette'
  Views = require 'common/mainviews'
  MainBus = require 'msgbus'

  initialize_page = (appmodel, msgbus) ->
    console.log 'initialize_page'
    layout = new Views.MainPageLayout
    layout.on 'show', =>
      navbar = new Views.BootstrapNavBarView
        model: appmodel
      msgbus.vent.trigger 'main-navbar:show', navbar
      
    msgbus.vent.trigger 'mainpage:show', layout


  set_init_page_handler = (msgbus) ->
    msgbus.commands.setHandler 'mainpage:init', (appmodel) ->
      initialize_page(appmodel, msgbus)

  display_main_navbar_contents = (msgbus) ->
    user = msgbus.reqres.request 'get-current-user'
    window.ffuser = user
    view = new Views.UserMenuView
      model: user
    window.uview = view
    msgbus.vent.trigger 'user-menu:show', view

  set_main_navbar_handler = (msgbus) ->
    msgbus.vent.on 'main-navbar:displayed', (view) ->
      display_main_navbar_contents msgbus
      
  module.exports =
    set_init_page_handler: set_init_page_handler
    set_main_navbar_handler: set_main_navbar_handler