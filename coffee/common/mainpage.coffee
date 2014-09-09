define (require, exports, module) ->
  Backbone = require 'backbone'
  Marionette = require 'marionette'
  Views = require 'common/mainviews'
  MainBus = require 'msgbus'

  initialize_page = (appmodel, msgbus) ->
    console.log 'initialize_page'
    layout = new Views.MainPageLayout
    layout.on 'show', =>
      #console.log 'layout show---->'
      navbar = new Views.BootstrapNavBarView
        model: appmodel
      msgbus.vent.trigger 'appregion:navbar:show', navbar
      #console.log 'triggered appregion:navbar:show'
    #console.log 'added layout event callback'
    msgbus.vent.trigger 'appregion:mainview:show', layout


  set_init_page_handler = (msgbus) ->
    msgbus.commands.setHandler 'mainpage:init', (appmodel) ->
      initialize_page(appmodel, msgbus)

  display_main_navbar_contents = (msgbus) ->
    #console.log 'called display_main_navbar_contents'
    user = msgbus.reqres.request 'get-current-user'
    view = new Views.UserMenuView
      model: user
    #window.uview = view
    msgbus.vent.trigger 'appregion:usermenu:show', view

  set_main_navbar_handler = (msgbus) ->
    msgbus.vent.on 'appregion:navbar:displayed', (view) ->
      #console.log 'appregion:navbar:displayed triggered'
      display_main_navbar_contents msgbus
      
  module.exports =
    set_init_page_handler: set_init_page_handler
    set_main_navbar_handler: set_main_navbar_handler
