define (require, exports, module) ->
  $ = require 'jquery'
  jQuery = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'
  bootstrap = require 'bootstrap'
  Marionette = require 'marionette'

  
  MSGBUS = require 'msgbus'
  Models = require 'models'
  
  require 'mainpage'
  require 'frontdoor/main'
  require 'demoapp/main'
  
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
      
    app.msgbus = MSGBUS

    app.addInitializer ->
      # execute code to generate basic page
      # layout
      MSGBUS.commands.execute 'mainpage:init'

      # then setup the routes
      MSGBUS.commands.execute 'frontdoor:route'
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
    
  
  module.exports = app
  
    
