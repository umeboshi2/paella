define (require, exports, module) ->
  Backbone = require 'backbone'
  Marionette = require 'marionette'
  MSGBUS = require 'msgbus'
  Views = require 'views/mainviews'

  
  main_menu_data =
    tagclass: 'main-menu'
    label: 'Main'
    entries: [
      {
        name: 'Home'
        url: '#'
      }
      {
        name: 'Simple RSS'
        url: '#simplerss'
      }
      {
        name: 'Jellyfish'
        url: '#jellyfish'
      }
      ]

  MainMenuModel = new Backbone.Model main_menu_data


  display_mainbar_contents = (view) ->
    mainmenu = new Views.MenuView
      model: MainMenuModel
    MSGBUS.events.trigger 'main-menu:show', mainmenu
    console.log 'triggered main-menu:show'
    #console.log $('#main-menu').addClass('action-button')
    
    
  initialize_page = () ->
    console.log 'initialize_page'
    layout = new Views.MainPageLayout
    layout.on 'show', =>
      view = new Views.MainPageView
      mainbar = new Views.MainBarView
      MSGBUS.events.trigger 'mainbar:show', mainbar

      user = MSGBUS.reqres.request 'current:user'

    MSGBUS.events.trigger 'mainpage:show', layout


  
  MSGBUS.events.on 'mainbar:displayed', (view) ->
    console.log 'new handle for mainbar:displayed'
    console.log 'mainbar should be visible'
    
  MSGBUS.commands.setHandler 'mainpage:init', () ->
    initialize_page()
    