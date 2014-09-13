define (require, exports, module) ->
  Backbone = require 'backbone'
  Marionette = require 'marionette'
  Views = require 'common/mainviews'

  initialize_page = (appmodel, msgbus, layout, navbar) ->
    console.log "initialize_page #{layout} #{navbar}"
    window.lllayout = layout
    layout = new layout
    layout.on 'show', =>
      #console.log 'layout show---->'
      navbar = new navbar
        model: appmodel
      msgbus.vent.trigger 'appregion:navbar:show', navbar
      #console.log 'triggered appregion:navbar:show'
    #console.log 'added layout event callback'
    msgbus.vent.trigger 'appregion:mainview:show', layout


  set_init_page_handler = (msgbus, pagename, layout, navbar) ->
    initsignal = "#{pagename}:init"
    displaysignal = "#{pagename}:displayed"
    console.log "#{initsignal} and #{displaysignal} defined"
    msgbus.commands.setHandler initsignal, (appmodel) =>
      initialize_page appmodel, msgbus, layout, navbar
      msgbus.vent.trigger displaysignal
      console.log "Triggered #{displaysignal}"
      
  set_mainpage_init_handler = (msgbus) =>
    layout = Views.MainPageLayout
    navbar = Views.BootstrapNavBarView
    set_init_page_handler msgbus, 'mainpage', layout, navbar

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

  # These are handlers to retrieve the colors
  # from the navbars, and are used to create
  # the default color for the fullcalendar
  # events.
  set_get_navbar_color_handlers = (msgbus) ->
    msgbus.reqres.setHandler 'get-navbar-color', ->
      navbar = $ '#main-navbar'
      navbar.css 'color'
    msgbus.reqres.setHandler 'get-navbar-bg-color', ->
      navbar = $ '#main-navbar'
      navbar.css 'background-color'
      
  module.exports =
    set_init_page_handler: set_init_page_handler
    set_mainpage_init_handler: set_mainpage_init_handler
    set_main_navbar_handler: set_main_navbar_handler
    set_get_navbar_color_handlers: set_get_navbar_color_handlers
    
