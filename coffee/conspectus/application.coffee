define (require, exports, module) ->
  $ = require 'jquery'
  jQuery = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'
  bootstrap = require 'bootstrap'
  Marionette = require 'marionette'

  
  MSGBUS = require 'msgbus'
  Models = require 'models'
  
  require 'common/mainpage'
  
  require 'frontdoor/main'
  require 'wiki/main'
  require 'bumblr/main'
  require 'hubby/main'

  appmodel = new Backbone.Model
    brand:
      name: 'Conspectus'
      url: '#'
    apps:
      [
        {
          name: 'Wiki'
          url: '#wiki'
        }
        {
          name: 'Bumblr'
          url: '#bumblr'
        }
        {
          name: 'Hubby'
          url: '#hubby'
        }
      ]
                
  prepare_app = (app) ->
    app.addRegions
      mainview: 'body'

      navbar: '#main-navbar'
      footer: '#footer'
      
      sidebar: '#sidebar'
      content: '#main-content'
      
    app.on 'start', ->
      console.log "start event being handled"
      Backbone.history.start() unless Backbone.history.started

    # I really only use this in the console
    # when app is attached to window
    app.msgbus = MSGBUS

    app.addInitializer ->
      # execute code to generate basic page
      # layout
      #window.appmodel = appmodel
      MSGBUS.commands.execute 'mainpage:init', appmodel

      # then setup the routes
      MSGBUS.commands.execute 'frontdoor:route'
      MSGBUS.commands.execute 'wiki:route'
      MSGBUS.commands.execute 'bumblr:route'
      MSGBUS.commands.execute 'hubby:route'
      
    # connect events
    MSGBUS.events.on 'mainpage:show', (view) =>
      console.log 'mainpage:show called'
      app.mainview.show view
      
    MSGBUS.events.on 'main-menu:show', (view) =>
      console.log 'main-menu:show called'
      app.main_menu.show view
      

    MSGBUS.events.on 'sidebar:show', (view) =>
      console.log 'sidebar:show called'
      app.sidebar.show view

    MSGBUS.events.on 'sidebar:close', () =>
      console.log 'sidebar:close called'
      if 'sidebar' in app
        app.sidebar.destroy()

    MSGBUS.events.on 'main-navbar:show', (view) =>
      console.log 'main-navbar:show called'
      app.navbar.show view
      
    MSGBUS.events.on 'rcontent:show', (view) =>
      console.log 'rcontent:show called'
      app.content.show view
      
    MSGBUS.events.on 'rcontent:close', () =>
      console.log "rcontent:close called"
      if app.content != undefined
        console.log app.content
        if app.content.currentView != undefined
          console.log app.content.currentView
          app.content.empty()
      
            
      
  app = new Marionette.Application()
    
  app.ready = false

  prepare_app app
  app.ready = true

  
  # These are handlers to retrieve the colors
  # from the navbars, and are used to create
  # the default color for the fullcalendar
  # events.
  MSGBUS.reqres.setHandler 'mainpage:navbar-color', ->
    navbar = $ '#main-navbar'
    navbar.css 'color'
    
  MSGBUS.reqres.setHandler 'mainpage:navbar-bg-color', ->
    navbar = $ '#main-navbar'
    navbar.css 'background-color'
    
  
  module.exports = app
  
    
