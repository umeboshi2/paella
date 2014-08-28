define (require, exports, module) ->
  Backbone = require 'backbone'
  Marionette = require 'marionette'
  MSGBUS = require 'msgbus'
  Views = require 'common/mainviews'

  initialize_page = (appmodel) ->
    console.log 'initialize_page'
    layout = new Views.MainPageLayout
    layout.on 'show', =>
      navbar = new Views.BootstrapNavBarView
        model: appmodel
      MSGBUS.events.trigger 'main-navbar:show', navbar
      
    MSGBUS.events.trigger 'mainpage:show', layout


  
  MSGBUS.commands.setHandler 'mainpage:init', (appmodel) ->
    initialize_page(appmodel)
    