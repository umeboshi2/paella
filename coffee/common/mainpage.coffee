define (require, exports, module) ->
  Backbone = require 'backbone'
  Marionette = require 'marionette'
  Views = require 'common/mainviews'
  MainBus = require 'msgbus'

  initialize_page = (appmodel) ->
    console.log 'initialize_page'
    layout = new Views.MainPageLayout
    layout.on 'show', =>
      navbar = new Views.BootstrapNavBarView
        model: appmodel
      MainBus.vent.trigger 'main-navbar:show', navbar
      
    MainBus.vent.trigger 'mainpage:show', layout


  
  MainBus.commands.setHandler 'mainpage:init', (appmodel) ->
    initialize_page(appmodel)
    