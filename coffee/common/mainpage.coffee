define (require, exports, module) ->
  Backbone = require 'backbone'
  Marionette = require 'marionette'
  Views = require 'common/mainviews'

  initialize_page = (app, msgbus, layout, navbar) ->
    #console.log "initialize_page #{layout} #{navbar}"
    layout = new layout
    layout.on 'show', =>
      #console.log 'layout show---->'
      navbar = new navbar
        model: app.appmodel
      app.navbar.show navbar
    #console.log 'added layout event callback'
    app.mainview.show layout


  set_init_page_handler = (msgbus, pagename, layout, navbar) ->
    initsignal = "#{pagename}:init"
    displaysignal = "#{pagename}:displayed"
    #console.log "#{initsignal} and #{displaysignal} defined"
    msgbus.commands.setHandler initsignal, (appmodel) =>
      app = msgbus.reqres.request 'main:app:object'
      initialize_page app, msgbus, layout, navbar
      msgbus.vent.trigger displaysignal
      #console.log "Triggered #{displaysignal}"
      
  set_mainpage_init_handler = (msgbus) =>
    layout = Views.MainPageLayout
    navbar = Views.BootstrapNavBarView
    set_init_page_handler msgbus, 'mainpage', layout, navbar

  display_main_navbar_contents = (msgbus) ->
    console.log 'called display_main_navbar_contents'
    user = msgbus.reqres.request 'get-current-user'
    view = new Views.UserMenuView
      model: user
    #window.uview = view
    app = msgbus.reqres.request 'main:app:object'
    app.usermenu.show view

  set_main_navbar_handler = (msgbus) ->
    msgbus.vent.on 'appregion:navbar:displayed', ->
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
    
